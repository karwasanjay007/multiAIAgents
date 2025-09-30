"""YouTube research agent that fetches video metadata, transcripts, and summaries."""
from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import time
from functools import lru_cache
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import requests
from requests import Session
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

try:
    import whisper  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    whisper = None

try:
    from yt_dlp import YoutubeDL  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    YoutubeDL = None

from src.graph.state import ResearchState
from src.utils.config_loader import get_youtube_api_key
from src.utils.llm_registry import invoke_llm, zero_metrics
from src.utils.structured_data import build_structured_record

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "youtube"
DATA_DIR.mkdir(parents=True, exist_ok=True)

_FFMPEG_PATH_HINT = os.getenv("FFMPEG_BIN")
if _FFMPEG_PATH_HINT and _FFMPEG_PATH_HINT not in os.environ.get("PATH", ""):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + _FFMPEG_PATH_HINT

logger = logging.getLogger(__name__)

_PUBLISHED_AFTER_DAYS = 365
_ENABLE_WHISPER_FALLBACK = os.getenv("ENABLE_WHISPER_FALLBACK", "0") == "1"
_WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
_whisper_model: Optional[Any] = None

_SUMMARY_PROMPT_PATH = Path(__file__).resolve().parents[1] / 'prompts' / 'youtube_summary_prompt.txt'
_DEFAULT_SUMMARY_PROMPT = (
    'You are summarising insights from a YouTube video.\n'
    'Title: {title}\n'
    'Channel: {channel}\n'
    'URL: {url}\n\n'
    'Provide a concise summary, three bullet highlights, and recommended actions if applicable.'
)

_session: Optional[Session] = None



@lru_cache(maxsize=1)
def _load_summary_prompt() -> str:
    """Load the YouTube summary prompt template, cached across runs."""
    if _SUMMARY_PROMPT_PATH.exists():
        return _SUMMARY_PROMPT_PATH.read_text(encoding="utf-8")
    return _DEFAULT_SUMMARY_PROMPT


def _ensure_ffmpeg_available() -> Optional[str]:
    """Return the ffmpeg path if available, suggesting FFMPEG_BIN otherwise."""
    ffmpeg_path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if ffmpeg_path is None:
        if _FFMPEG_PATH_HINT:
            logger.warning("FFmpeg not found on PATH even after appending FFMPEG_BIN=%s", _FFMPEG_PATH_HINT)
        else:
            logger.warning("FFmpeg not found on PATH; set FFMPEG_BIN env variable or install ffmpeg")
    return ffmpeg_path


def _ensure_whisper_model():
    """Initialise and cache the Whisper model used for transcript fallback."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    if whisper is None:  # pragma: no cover - optional dependency
        raise RuntimeError("whisper_not_installed")
    logger.info("Loading Whisper model '%s' for YouTube fallback", _WHISPER_MODEL_NAME)
    _whisper_model = whisper.load_model(_WHISPER_MODEL_NAME)
    return _whisper_model


def _transcribe_with_whisper(video_id: str, video_url: str) -> Tuple[str, str, Optional[str]]:
    """Download video audio and attempt transcription via Whisper."""
    if not _ENABLE_WHISPER_FALLBACK:
        return "", "", "whisper_fallback_disabled"
    if whisper is None:
        return "", "", "whisper_not_installed"
    if YoutubeDL is None:
        return "", "", "yt_dlp_not_installed"
    ffmpeg_path = _ensure_ffmpeg_available()
    if ffmpeg_path is None:
        return "", "", "ffmpeg_not_found"
    try:
        model = _ensure_whisper_model()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Whisper model load failed: %s", exc)
        return "", "", f"whisper_load_error: {exc}"
    try:
        with tempfile.TemporaryDirectory(prefix=f"yt_whisper_{video_id}_") as tmpdir:
            target = Path(tmpdir) / "%(id)s.%(ext)s"
            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "outtmpl": str(target),
            }
            with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                ydl.download([video_url])
            candidates = sorted(Path(tmpdir).glob("*"), key=lambda p: p.stat().st_size, reverse=True)
            audio_file = next((path for path in candidates if path.is_file()), None)
            if audio_file is None:
                return "", "", "audio_download_failed"
            logger.debug("Transcribing %s via Whisper from %s", video_id, audio_file)
            try:
                result = model.transcribe(str(audio_file), fp16=False)  # type: ignore[call-arg]
            except FileNotFoundError as exc:
                logger.exception("Whisper could not invoke ffmpeg for %s: %s", video_id, exc)
                return "", "", "ffmpeg_execution_failed"
            text_result = result.get("text") or ""
            text = text_result.strip()
            language = result.get("language") or "unknown"
            if not text:
                return "", language, "whisper_returned_empty_text"
            return text, language, None
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Whisper transcription failed for %s: %s", video_id, exc)
        return "", "", f"whisper_error: {exc}"


def _get_session() -> Session:
    """Return a singleton HTTP session for YouTube API calls."""
    global _session
    if _session is None:
        _session = Session()
        _session.headers.update({"Accept": "application/json"})
    return _session


SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

_MAX_RESULTS_SIMPLE = 2
_MAX_RESULTS_EXTENDED = 6
_SUMMARY_MAX_CHARS = 5000


def _parse_duration(iso_duration: str) -> str:
    """Convert YouTube ISO 8601 durations to a human-readable clock string."""
    if not iso_duration:
        return "Unknown"
    hours = minutes = seconds = 0
    current = ""
    for ch in iso_duration[2:]:
        if ch.isdigit():
            current += ch
        elif ch == "H":
            hours = int(current or 0)
            current = ""
        elif ch == "M":
            minutes = int(current or 0)
            current = ""
        elif ch == "S":
            seconds = int(current or 0)
            current = ""
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _search_videos(api_key: str, query: str, max_results: int, extra_factor: int = 3) -> List[Dict]:
    """Run the YouTube search API and return candidate video metadata."""
    published_after = (datetime.utcnow() - timedelta(days=_PUBLISHED_AFTER_DAYS)).isoformat("T") + "Z"
    params = {
        "key": api_key,
        "q": query,
        "type": "video",
        "part": "id,snippet",
        "maxResults": min(50, max_results * max(1, extra_factor)),
        "relevanceLanguage": "en",
        "order": "relevance",
        "videoCaption": "closedCaption",
        "publishedAfter": published_after,
        "safeSearch": "moderate",
    }
    resp = _get_session().get(SEARCH_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    items: List[Dict] = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if video_id:
            items.append(
                {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                    "thumbnails": snippet.get("thumbnails", {}),
                }
            )
    return items[: max_results * max(1, extra_factor)]


def _fetch_video_details(api_key: str, video_ids: List[str]) -> Dict[str, Dict]:
    """Fetch duration and statistics for the supplied set of video IDs."""
    if not video_ids:
        return {}
    params = {
        "key": api_key,
        "id": ",".join(video_ids),
        "part": "contentDetails,statistics",
        "maxResults": len(video_ids),
    }
    resp = _get_session().get(VIDEOS_URL, params=params, timeout=20)
    resp.raise_for_status()
    details = {}
    for item in resp.json().get("items", []):
        video_id = item.get("id")
        if not video_id:
            continue
        content_details = item.get("contentDetails", {})
        stats = item.get("statistics", {})
        details[video_id] = {
            "duration": _parse_duration(content_details.get("duration")),
            "view_count": stats.get("viewCount"),
            "like_count": stats.get("likeCount"),
            "comment_count": stats.get("commentCount"),
        }
    return details


def _fetch_transcript(video_id: str) -> Tuple[str, str, Optional[str]]:
    """Pull captions for *video_id* using youtube-transcript-api when available."""
    def _segments_to_text(segments: List[Dict[str, Any]]) -> str:
        return " ".join(segment.get("text", "") for segment in segments if segment.get("text")).strip()

    try:
        if hasattr(YouTubeTranscriptApi, "list_transcripts"):
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript_obj = None
            try:
                transcript_obj = transcripts.find_transcript(["en"])
            except NoTranscriptFound:
                try:
                    transcript_obj = transcripts.find_generated_transcript(["en"])
                except NoTranscriptFound:
                    transcript_obj = None
            if transcript_obj is None:
                for candidate in transcripts:
                    if getattr(candidate, "language_code", "").startswith("en"):
                        transcript_obj = candidate
                        break
            if transcript_obj is None:
                for candidate in transcripts:
                    if getattr(candidate, "is_translatable", False):
                        try:
                            transcript_obj = candidate.translate("en")
                            break
                        except Exception:
                            continue
            if transcript_obj is None:
                return "", "", "no_transcript_available"
            segments = transcript_obj.fetch()
            language = getattr(transcript_obj, "language_code", getattr(transcript_obj, "language", "unknown"))
            text_content = _segments_to_text(segments)
            return text_content, language or "unknown", None

        logger.debug("YouTubeTranscriptApi.list_transcripts unavailable; attempting legacy get_transcript for %s", video_id)
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])  # type: ignore[attr-defined]
        text_content = _segments_to_text(segments)
        return text_content, "en", None
    except (TranscriptsDisabled, NoTranscriptFound) as exc:
        logger.info("Transcript unavailable for %s: %s", video_id, exc)
        return "", "", str(exc)
    except AttributeError as exc:
        logger.info("YouTubeTranscriptApi get_transcript unavailable for %s: %s", video_id, exc)
        return "", "", f"attr_error: {exc}"
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Transcript fetch failed for %s", video_id)
        return "", "", str(exc)


def _summarize_video(title: str, channel: str, transcript: str, url: str) -> Tuple[str, Any]:
    """Summarise a video's transcript with the LLM-based youtube summarizer."""
    if not transcript:
        return "No transcript available.", zero_metrics("youtube_summarizer")
    prompt_template = _load_summary_prompt()
    prompt = prompt_template.format(
        title=title or 'Unknown title',
        channel=channel or 'Unknown channel',
        url=url,
    )
    excerpt = transcript[:_SUMMARY_MAX_CHARS]
    combined = f"{prompt}\n\nTranscript:\n{excerpt}"
    response, metrics = invoke_llm("youtube_summarizer", combined)
    return response.content.strip(), metrics


def analyze_youtube(state: ResearchState) -> Dict[str, Dict]:
    """Collect, transcribe, and summarise relevant YouTube content for *state*."""
    start = time.time()
    api_key = get_youtube_api_key()
    topic = state.get("topic", "")
    mode = state.get("mode", "extended")

    if not api_key:
        elapsed = time.time() - start
        return {
            "youtube_results": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "YOUTUBE_API_KEY not configured"},
            }
        }

    max_results = _MAX_RESULTS_SIMPLE if mode == "simple" else _MAX_RESULTS_EXTENDED

    try:
        search_results = _search_videos(api_key, topic, max_results, extra_factor=3)
        search_results.sort(key=lambda item: item.get("published_at", ""), reverse=True)
    except Exception as exc:
        elapsed = time.time() - start
        return {
            "youtube_results": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": f"YouTube search failed: {exc}"},
            }
        }

    video_ids = [item["video_id"] for item in search_results]
    try:
        video_details = _fetch_video_details(api_key, video_ids)
    except Exception:
        video_details = {}

    run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    run_dir = DATA_DIR / run_id
    transcripts_dir = run_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    summaries: List[Dict[str, Any]] = []
    metadata_records: List[Dict[str, Any]] = []

    total_tokens = 0
    total_cost = 0.0
    total_summary_time = 0.0

    for video in search_results:
        if len(summaries) >= max_results:
            break
        video_id = video["video_id"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        metadata = video_details.get(video_id, {})

        transcript_text, language, fetch_error = _fetch_transcript(video_id)
        transcript_source = "youtube_api" if transcript_text else None
        transcript_error = fetch_error
        debug_notes: List[str] = []
        if fetch_error:
            debug_notes.append(f"youtube_api: {fetch_error}")
        if not transcript_text:
            fallback_text, fallback_language, whisper_error = _transcribe_with_whisper(video_id, url)
            if fallback_text:
                transcript_text = fallback_text
                language = fallback_language or language
                transcript_source = "whisper"
                transcript_error = None
            elif whisper_error:
                transcript_error = f"{transcript_error + ' | ' if transcript_error else ''}{whisper_error}"
                debug_notes.append(f"whisper: {whisper_error}")

        transcript_path = None
        if transcript_text:
            transcript_path = transcripts_dir / f"{video_id}.txt"
            transcript_path.write_text(transcript_text, encoding="utf-8")

        language_label = language or "unknown"
        summary_text = "No transcript available."
        metrics = zero_metrics("youtube_summarizer")
        if transcript_text and (not language or language.startswith('en')):
            summary_text, metrics = _summarize_video(
                video.get("title", ""),
                video.get("channel", ""),
                transcript_text,
                url,
            )
        else:
            if transcript_text and not language_label.startswith('en'):
                debug_notes.append(f"skipped summarization for non-English language: {language_label}")
                summary_text = f"Transcript available but skipped summarization due to language ({language_label})."
            elif not transcript_text:
                summary_text = "No transcript available." if not transcript_error else f"No transcript available ({transcript_error})."

        total_tokens += metrics.total_tokens
        total_cost += metrics.cost
        total_summary_time += metrics.duration

        structured = build_structured_record(
            title=video.get("title"),
            content=transcript_text[:1000] if transcript_text else None,
            summary=summary_text,
            source=url,
            published_date=video.get("published_at"),
            authors=video.get("channel"),
        )

        item_metadata = {
            "video_id": video_id,
            "duration": metadata.get("duration", "Unknown"),
            "views": metadata.get("view_count"),
            "likes": metadata.get("like_count"),
            "comments": metadata.get("comment_count"),
            "language": language_label,
            "transcript_path": str(transcript_path) if transcript_path else None,
            "transcript_source": transcript_source,
            "transcript_error": transcript_error,
        }
        if debug_notes:
            item_metadata["debug"] = debug_notes

        logger.debug("YouTube video %s transcript source=%s language=%s error=%s", video_id, item_metadata.get("transcript_source"), language_label, transcript_error)

        video_index = len(summaries) + 1
        summaries.append({
            "name": f"video_{video_index}",
            "items": [structured],
            "metadata": item_metadata,
        })
        metadata_records.append({
            "video": video,
            "details": item_metadata,
            "summary": summary_text,
            "transcript_path": str(transcript_path) if transcript_path else None,
        })

    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata_records, ensure_ascii=False, indent=2), encoding="utf-8")

    elapsed = time.time() - start

    return {
        "youtube_results": {
            "sources": summaries,
            "elapsed": elapsed,
            "tokens": total_tokens,
            "cost": total_cost,
            "details": {
                "run_id": run_id,
                "chunking_time": elapsed - total_summary_time,
                "summary_time": total_summary_time,
                "mode": mode,
                "video_count": len(summaries),
                "metadata_path": str(metadata_path),
            },
        }
    }

