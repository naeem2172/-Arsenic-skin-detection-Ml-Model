"""Application settings from environment variables."""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    """Configuration class for the chatbot."""

    # Ollama (free local LLM - no API key needed)
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # LLM
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1024"))

    # Language
    SUPPORTED_LANGUAGES: list = os.getenv("SUPPORTED_LANGUAGES", "en,bn").split(",")

    # Disclaimer
    DISCLAIMER_EN: str = (
        "This chatbot provides general information only and is not a substitute for professional medical advice. "
        "Always consult a healthcare provider for diagnosis and treatment."
    )
    DISCLAIMER_BN: str = (
        "এই চ্যাটবট শুধুমাত্র সাধারণ তথ্য প্রদান করে এবং পেশাদার চিকিৎসা পরামর্শের বিকল্প নয়। "
        "নির্ণয় এবং চিকিৎসার জন্য সর্বদা একজন স্বাস্থ্যসেবা প্রদানকারীর সাথে পরামর্শ করুন।"
    )

    # Emergency contacts
    EMERGENCY_CONTACTS: dict = {
        "en": {
            "title": "Emergency Contacts",
            "national_poison": "National Poison Control: 1-800-222-1222",
            "health_helpline": "Health Helpline: 16263 (Bangladesh)",
        },
        "bn": {
            "title": "জরুরি যোগাযোগ",
            "national_poison": "জাতীয় বিষ নিয়ন্ত্রণ: ১-৮০০-২২২-১২২২",
            "health_helpline": "স্বাস্থ্য হেল্পলাইন: ১৬২৬৩ (বাংলাদেশ)",
        },
    }


settings = Settings()
