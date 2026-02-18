from __future__ import annotations

import os

import httpx


LLM_URL = os.getenv("LLM_URL", "http://local-llm:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q4_K_M")


def summarize_risk(question: str, context: str) -> str:
    prompt = (
        "You are an air-gapped OT governance assistant. "
        "Use only the provided context to explain risk clearly and concisely.\n\n"
        f"Question: {question}\n\nContext:\n{context}\n"
    )
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(
                f"{LLM_URL}/api/generate",
                json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "No response generated")
    except Exception:
        return "Local LLM unavailable. Verify local-llm service and model preload in ./local_models."
