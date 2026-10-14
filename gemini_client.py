"""
Google Gemini Client for PayPal LXNORO Agent 04.
Integrates Google's official google-genai SDK to enhance natural-language shopping requests
into concise product search queries for Channel3 using gemini-3.1-flash-lite.
Strictly handles missing API keys, SDK import failures, and API errors with graceful fallback.
"""

import os
import logging

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.1-flash-lite"


def enhance_search_query_with_gemini(user_query: str) -> str:
    """
    Takes a natural-language user shopping request and uses Google Gemini Flash-Lite
    to convert it into a concise, effective product-search query for Channel3.
    Returns only the refined query text, or the original user_query if unavailable or on error.
    """
    if not isinstance(user_query, str) or not user_query.strip():
        return user_query

    clean_query = user_query.strip()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        logger.debug("GEMINI_API_KEY is not configured; falling back to original query.")
        return clean_query

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning("google-genai SDK is not installed or available; falling back to original query.")
        return clean_query

    try:
        client = genai.Client(
            api_key=api_key.strip(),
            http_options={"timeout": 30000}
        )
        prompt = (
            "Convert the following customer shopping request into a concise, high-value product search query "
            "suitable for an e-commerce catalog API (maximum 8 words). "
            "Return ONLY the search query text with no explanations, punctuation marks, or markdown:\n\n"
            f"\"{clean_query}\""
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=64,
            ),
        )

        if response and hasattr(response, "text") and response.text:
            refined = response.text.strip().strip('"').strip("'")
            if (
                refined
                and len(refined) <= 120
                and len(refined.split()) <= 8
                and "\n" not in refined
                and "\r" not in refined
            ):
                return refined

    except Exception as exc:
        logger.error("Gemini API request failed (%s); falling back to original query.", type(exc).__name__)

    return clean_query
