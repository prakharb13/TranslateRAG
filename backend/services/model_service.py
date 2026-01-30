from typing import Optional, List

import ollama

from backend.config import OLLAMA_BASE_URL, MODEL_NAME

LANGUAGE_CODES = {
    "Arabic": "ar", "Chinese (Simplified)": "zh", "Czech": "cs",
    "Dutch": "nl", "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Polish": "pl", "Portuguese": "pt", "Russian": "ru", "Spanish": "es",
    "Swedish": "sv", "Thai": "th", "Turkish": "tr", "Ukrainian": "uk",
    "Vietnamese": "vi",
}

_client = ollama.Client(host=OLLAMA_BASE_URL)


def _get_code(language: str) -> str:
    return LANGUAGE_CODES.get(language, language[:2].lower())


def translate(
    text: str,
    source_language: str,
    target_language: str,
    context: Optional[str] = None,
) -> str:
    src_code = _get_code(source_language)
    tgt_code = _get_code(target_language)

    system_prompt = (
        f"You are a professional {source_language} ({src_code}) to "
        f"{target_language} ({tgt_code}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the "
        f"original {source_language} text while adhering to {target_language} "
        f"grammar, vocabulary, and cultural sensitivities. "
        f"Produce only the {target_language} translation, without any additional "
        f"explanations or commentary."
    )

    user_content = ""
    if context:
        user_content += (
            f"Reference material for domain-specific terminology:\n{context}\n\n"
            f"Use the above reference for accurate specialized terms.\n\n"
        )
    user_content += (
        f"Please translate the following {source_language} text into "
        f"{target_language}:\n\n{text}"
    )

    response = _client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": system_prompt + "\n\n" + user_content}],
    )
    return response["message"]["content"].strip()


def answer_question(
    question: str,
    context: str,
    source_language: str,
    target_language: str,
) -> str:
    src_code = _get_code(source_language)
    tgt_code = _get_code(target_language)

    prompt = (
        f"You are a professional {source_language} ({src_code}) to "
        f"{target_language} ({tgt_code}) translator. "
        f"You are given document excerpts and a question. "
        f"Answer the question using the provided context, and write your answer "
        f"in {target_language} ({tgt_code}). "
        f"If the context does not contain enough information, say so in {target_language}.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer in {target_language}:"
    )

    response = _client.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
