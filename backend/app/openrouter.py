from __future__ import annotations
import base64, json, re, time
from typing import Any
import httpx
from .config import (
    AI_ENABLED, DEMO_MODE, OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL,
    OPENROUTER_SITE_URL, OPENROUTER_APP_NAME, OPENROUTER_TIMEOUT_SECONDS,
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_BASE_URL, openrouter_configured, gemini_configured,
)

class AIUnavailable(Exception):
    pass

def _extract_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = str(value or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.M)
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("AI response must be a JSON object")
    return parsed

class OpenRouterClient:
    """OpenRouter free-model provider, with an optional Gemini fallback."""
    async def _openrouter(self, system: str, user: str, images: list[tuple[str, bytes]] | None = None) -> dict[str, Any]:
        if not openrouter_configured():
            raise AIUnavailable("OpenRouter is not configured with an explicitly free model")
        content: list[dict[str, Any]] = [{"type": "text", "text": user}]
        for mime, data in images or []:
            b64 = base64.b64encode(data).decode()
            content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
        payload = {"model": OPENROUTER_MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}], "temperature": 0.1}
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": OPENROUTER_SITE_URL, "X-Title": OPENROUTER_APP_NAME}
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
                response = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
            text = body["choices"][0]["message"]["content"]
            if isinstance(text, list):
                text = "".join(part.get("text", "") for part in text if isinstance(part, dict))
            result = _extract_json(text)
            result["_learnlens_provider"] = "OpenRouter"
            print(f"AI_PROVIDER_OK provider=OpenRouter elapsed_ms={(time.perf_counter()-started)*1000:.1f}", flush=True)
            return result
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            print(f"AI_PROVIDER_ERROR provider=OpenRouter elapsed_ms={(time.perf_counter()-started)*1000:.1f} error_type={type(exc).__name__}", flush=True)
            raise AIUnavailable("OpenRouter request failed or returned invalid JSON") from exc

    async def _gemini(self, system: str, user: str, images: list[tuple[str, bytes]] | None = None) -> dict[str, Any]:
        if not gemini_configured():
            raise AIUnavailable("Gemini fallback is not configured")
        parts: list[dict[str, Any]] = [{"text": f"SYSTEM INSTRUCTIONS:\n{system}\n\nUSER REQUEST:\n{user}"}]
        for mime, data in images or []:
            parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}})
        payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}}
        headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
                response = await client.post(f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent", headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
            parts_out = body["candidates"][0]["content"]["parts"]
            text = "".join(str(part.get("text", "")) for part in parts_out if isinstance(part, dict))
            result = _extract_json(text)
            result["_learnlens_provider"] = "Gemini"
            print(f"AI_PROVIDER_OK provider=Gemini elapsed_ms={(time.perf_counter()-started)*1000:.1f}", flush=True)
            return result
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            print(f"AI_PROVIDER_ERROR provider=Gemini elapsed_ms={(time.perf_counter()-started)*1000:.1f} error_type={type(exc).__name__}", flush=True)
            raise AIUnavailable("Gemini request failed or returned invalid JSON") from exc

    async def complete_json(self, system: str, user: str, images: list[tuple[str, bytes]] | None = None) -> dict[str, Any]:
        errors = []
        providers = []
        if openrouter_configured(): providers.append(self._openrouter)
        if gemini_configured(): providers.append(self._gemini)
        if not providers:
            raise AIUnavailable("No AI provider is configured. Add a free-tier OpenRouter or Gemini key, or use the clearly labelled demo flow.")
        for provider in providers:
            try:
                return await provider(system, user, images)
            except AIUnavailable as exc:
                errors.append(str(exc))
        raise AIUnavailable("All configured AI providers failed. " + "; ".join(errors))

client = OpenRouterClient()
