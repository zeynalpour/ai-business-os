METIS_BASE_URLS = {
    "gemini": "https://api.metisai.ir/api/v1/wrapper/gemini",
    "openai": "https://api.metisai.ir/api/v1/wrapper/openai",
    "grok":   "https://api.metisai.ir/api/v1/wrapper/grok",
}

def _get_base_url(model: str) -> str:
    if model.startswith("gemini"):
        return METIS_BASE_URLS["gemini"]
    if model.startswith("grok"):
        return METIS_BASE_URLS["grok"]
    return METIS_BASE_URLS["openai"]