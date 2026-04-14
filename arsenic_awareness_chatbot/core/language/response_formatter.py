"""Format responses with sources and disclaimers."""
from typing import List, Optional
from ..config.settings import settings


def format_response_with_sources(
    response: str,
    sources: Optional[List[dict]] = None,
    lang: str = "en",
) -> str:
    """Format response with source citations."""
    disclaimer = settings.DISCLAIMER_BN if lang == "bn" else settings.DISCLAIMER_EN
    result = response
    if sources:
        ref_label = "সূত্র:" if lang == "bn" else "Sources:"
        refs = "\n".join(
            f"- {s.get('source', 'Unknown')} ({s.get('category', '')})"
            for s in sources[:5]
        )
        result += f"\n\n{ref_label}\n{refs}"
    result += f"\n\n_{disclaimer}_"
    return result
