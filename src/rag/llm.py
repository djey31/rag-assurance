from __future__ import annotations
"""Couche d'abstraction du modèle.

Le code ne dépend pas d'un fournisseur : on peut comparer un modèle ouvert
en local (Ollama) et une API, sur les mêmes questions, en changeant une
variable d'environnement. C'est ce qui rend l'évaluation comparable.
"""
import httpx
from .config import settings

def generate(prompt: str, temperature: float = 0.0) -> str:
    p = settings.llm_provider
    if p == "ollama":
        r = httpx.post(f"{settings.ollama_host}/api/generate", timeout=180,
                       json={"model": settings.ollama_model, "prompt": prompt,
                             "stream": False, "options": {"temperature": temperature}})
        r.raise_for_status()
        return r.json()["response"]
    if p == "anthropic":
        r = httpx.post("https://api.anthropic.com/v1/messages", timeout=120,
                       headers={"x-api-key": settings.anthropic_api_key,
                                "anthropic-version": "2023-06-01"},
                       json={"model": settings.anthropic_model, "max_tokens": 1024,
                             "temperature": temperature,
                             "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    if p == "openai_compatible":
        r = httpx.post(f"{settings.openai_base_url}/chat/completions", timeout=120,
                       headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                       json={"model": settings.openai_model, "temperature": temperature,
                             "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise ValueError(f"Fournisseur inconnu : {p}")
