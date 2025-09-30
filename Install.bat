@echo off
echo Installing all required packages...
python -m pip install --upgrade pip
python -m pip install aiohttp
python -m pip install youtube-transcript-api
python -m pip install yt-dlp
python -m pip install langchain-community
python -m pip install langchain
python -m pip install langchain-openai
python -m pip install arxiv
python -m pip install newsapi-python
python -m pip install google-api-python-client
python -m pip install sentence-transformers
python -m pip install chromadb
python -m pip install lancedb
python -m pip install pyarrow
python -m pip install pandas
python -m pip install streamlit
python -m pip install python-dotenv
python -m pip install reportlab
python -m pip install requests
echo.
echo Installation complete!
echo Run: python run_streamlit.py
pause