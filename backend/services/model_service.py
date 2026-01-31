from typing import Optional, List
import time
import logging

import ollama

from backend.config import OLLAMA_BASE_URL, MODEL_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings from other libraries
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("ollama").setLevel(logging.ERROR)

LANGUAGE_CODES = {
    "Arabic": "ar", "Chinese (Simplified)": "zh", "Czech": "cs",
    "Dutch": "nl", "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Polish": "pl", "Portuguese": "pt", "Russian": "ru", "Spanish": "es",
    "Swedish": "sv", "Thai": "th", "Turkish": "tr", "Ukrainian": "uk",
    "Vietnamese": "vi",
}

_client = ollama.Client(host=OLLAMA_BASE_URL, timeout=600)
logger.info(f"🔌 Ollama client initialized - connecting to: {OLLAMA_BASE_URL}")
logger.info(f"🤖 Using model: {MODEL_NAME}")


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
        f"You are an intelligent assistant that handles both translation and question-answering. "
        f"You work with {source_language} ({src_code}) and {target_language} ({tgt_code}).\n\n"
        f"Instructions:\n"
        f"1. If the input is a question or request for information (e.g., 'tell me about...', 'what is...', 'explain...'), "
        f"   answer the question comprehensively using your knowledge directly in {target_language} ({tgt_code}).\n"
        f"2. If the input is a statement or regular text, simply translate it to {target_language}.\n"
        f"3. Always produce your final output in {target_language} ({tgt_code}) only.\n"
        f"4. For questions, provide detailed, informative answers (2-3 paragraphs minimum)."
    )

    user_content = ""
    if context:
        user_content += (
            f"Reference material for domain-specific terminology:\n{context}\n\n"
            f"Use the above reference for accurate specialized terms.\n\n"
        )
    user_content += (
        f"Process the following {source_language} input and provide the output in {target_language}:\n\n{text}"
    )

    full_prompt = system_prompt + "\n\n" + user_content

    logger.info("=" * 80)
    logger.info(f"📝 TRANSLATE REQUEST")
    logger.info(f"   Source: {source_language} → Target: {target_language}")
    logger.info(f"   Text length: {len(text)} chars")
    logger.info(f"   Has context: {bool(context)}")
    logger.info(f"   Full prompt length: {len(full_prompt)} chars")
    logger.info(f"   Prompt preview: {full_prompt[:200]}...")
    logger.info(f"🚀 Sending request to Ollama at {OLLAMA_BASE_URL}...")

    start_time = time.time()
    try:
        response = _client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": full_prompt}],
        )
        elapsed = time.time() - start_time

        result = response["message"]["content"].strip()
        logger.info(f"✅ Response received in {elapsed:.2f}s")
        logger.info(f"   Response length: {len(result)} chars")
        logger.info(f"   Response preview: {result[:200]}...")
        logger.info("=" * 80)

        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Request failed after {elapsed:.2f}s")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 80)
        raise


def answer_question(
    question: str,
    context: str,
    source_language: str,
    target_language: str,
) -> str:
    src_code = _get_code(source_language)
    tgt_code = _get_code(target_language)

    if context:
        prompt = (
            f"You are a knowledgeable assistant that answers questions in {target_language} ({tgt_code}). "
            f"You are given document excerpts and a question in {source_language} ({src_code}). "
            f"Answer the question using the provided context as your primary source, and write your answer "
            f"in {target_language} ({tgt_code}). "
            f"If the context does not contain enough information, you may use your general knowledge "
            f"to provide a helpful answer, but prioritize the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer in {target_language}:"
        )
    else:
        prompt = (
            f"You are a knowledgeable assistant that answers questions in {target_language} ({tgt_code}). "
            f"Answer the following question in {source_language} ({src_code}) using your general knowledge. "
            f"Provide your answer in {target_language} ({tgt_code}).\n\n"
            f"Question: {question}\n\n"
            f"Answer in {target_language}:"
        )

    logger.info("=" * 80)
    logger.info(f"💬 ASK QUESTION REQUEST")
    logger.info(f"   Source: {source_language} → Target: {target_language}")
    logger.info(f"   Question: {question[:100]}...")
    logger.info(f"   Has context: {bool(context)}")
    if context:
        logger.info(f"   Context length: {len(context)} chars")
    logger.info(f"   Full prompt length: {len(prompt)} chars")
    logger.info(f"   Prompt preview: {prompt[:300]}...")
    logger.info(f"🚀 Sending request to Ollama at {OLLAMA_BASE_URL}...")

    start_time = time.time()
    try:
        response = _client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.time() - start_time

        result = response["message"]["content"].strip()
        logger.info(f"✅ Response received in {elapsed:.2f}s")
        logger.info(f"   Response length: {len(result)} chars")
        logger.info(f"   Response preview: {result[:200]}...")
        logger.info("=" * 80)

        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Request failed after {elapsed:.2f}s")
        logger.error(f"   Error: {str(e)}")
        logger.error("=" * 80)
        raise
