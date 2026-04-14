"""Language detection for English, Bangla, and Banglish."""
import re
from typing import Optional


class LanguageDetector:
    """Detect language: English, Bangla (bn), or Banglish (Romanized Bangla)."""

    # Bangla Unicode range: \u0980-\u09FF
    BANGLA_PATTERN = re.compile(r"[\u0980-\u09FF]+")

    # Common Banglish words (Romanized)
    BANGLISH_WORDS = {
        "ami", "tumi", "kemon", "ache", "nai", "ki", "kemon", "valo", "kharap",
        "arsenic", "pani", "jol", "chikitsa", "rog", "daktar", "hospital",
        "amar", "tomar", "kno", "jodi", "tobe", "kintu", "karon", "jani",
        "bolo", "sunun", "dhonnobad", "aschi", "jacci", "korchi", "korbo",
    }

    # Common English medical/arsenic words
    ENGLISH_WORDS = {
        "arsenic", "water", "symptoms", "treatment", "doctor", "skin",
        "what", "how", "why", "when", "where", "which", "help", "please",
    }

    @classmethod
    def detect(cls, text: str) -> str:
        """
        Detect language from text.
        Returns: 'en' for English, 'bn' for Bangla/Banglish.
        """
        if not text or not text.strip():
            return "en"

        text_lower = text.lower().strip()
        bangla_chars = len(cls.BANGLA_PATTERN.findall(text))
        total_alpha = sum(1 for c in text if c.isalpha())

        # If significant Bangla Unicode, it's Bangla
        if total_alpha > 0 and bangla_chars / total_alpha > 0.3:
            return "bn"

        # Check for Banglish (Romanized Bangla)
        words = set(re.findall(r"\b[a-z]+\b", text_lower))
        banglish_count = sum(1 for w in words if w in cls.BANGLISH_WORDS)
        english_count = sum(1 for w in words if w in cls.ENGLISH_WORDS)

        # If more Banglish indicators, return bn
        if banglish_count > english_count and banglish_count >= 1:
            return "bn"

        return "en"
