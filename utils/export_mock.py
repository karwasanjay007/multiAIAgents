def export_to_pdf(results: dict):
    """Mock PDF export"""
    return f"PDF Mock: {results.get('query', 'N/A')}".encode()

def export_to_markdown(results: dict):
    """Mock Markdown export"""
    md = f"""# Research Results

## Query
{results.get('query', 'N/A')}

## Summary
{results.get('summary', 'N/A')}

## Findings
"""
    for idx, finding in enumerate(results.get('key_findings', []), 1):
        md += f"{idx}. {finding}\n"
    
    return md