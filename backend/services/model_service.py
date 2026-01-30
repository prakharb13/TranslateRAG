from typing import Optional, List

import ollama

from backend.config import OLLAMA_BASE_URL, MODEL_NAME


_client = ollama.Client(host=OLLAMA_BASE_URL)


def translate(
    text: str,
    source_language: str,
    target_language: str,
    context: Optional[str] = None,
) -> str:
    prompt_parts: List[str] = []

    if context:
        prompt_parts.append(
            f"Reference material for domain-specific terminology:\n{context}\n\n"
            "Use the above reference to ensure accurate translation of "
            "specialised terms.\n\n"
        )

    prompt_parts.append(
        f"Translate the following text from {source_language} to {target_language}.\n"
        f"Only output the translation, nothing else.\n\n"
        f"{text}"
    )

    prompt = "".join(prompt_parts)

    response = _client.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"].strip()


def answer_question(
    question: str,
    context: str,
    source_language: str,
    target_language: str,
) -> str:
    prompt = (
        f"You are given document excerpts in {source_language} and a question.\n"
        f"Answer the question using only the provided context.\n"
        f"Translate your answer into {target_language}.\n"
        f"If the context does not contain enough information, say so in {target_language}.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer in {target_language}:"
    )
    response = _client.generate(model=MODEL_NAME, prompt=prompt)
    return response["response"].strip()
