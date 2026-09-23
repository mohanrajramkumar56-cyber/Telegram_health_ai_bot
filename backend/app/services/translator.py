import logging

logger = logging.getLogger(__name__)

# Language detection heuristics (no external dependency)
def detect_lang(text: str) -> str:
    """Simple heuristic for Indian languages - works well for short health queries."""
    text_lower = text.lower()
    # Tamil
    if any(w in text_lower for w in [
        "vanakkam", "வணக்கம்", "நன்றி", "எப்படி", "என்", "உnga", "என்", "நான்",
        "வேண்டும்", "இல்லை", "அம்மா", "அப்பா", "சிகிச்சை", "நோய்", "மருத்துவம்"
    ]):
        return "ta"
    # Hindi (Devanagari + transliteration)
    if any(w in text_lower for w in [
        "namaste", "kaise", "kya", "hai", "main", "aap", "dhanyavaad", "mujhe",
        "chahiye", "nahi", "haan", "maafi", "dawa", "bimari", "ilaaj",
        "mujhe", "chaiye", "chahiye", "batao", "kaisa", "kaisi"
    ]) or any('\u0900' <= c <= '\u097f' for c in text):
        return "hi"
    # Bengali
    if any(w in text_lower for w in [
        "kemon", "achen", "ami", "apni", "dhonnobad", "janina", "jani",
        "bhalo", "khub", "chikitsha", "rog", "oushod"
    ]):
        return "bn"
    return "en"


class OfflineTranslator:
    def __init__(self):
        self._translators = {}
        self._initialized = False

    def _init_translators(self):
        """Lazy initialization of argos-translate."""
        if self._initialized:
            return
        try:
            import argostranslate.package
            import argostranslate.translate

            # Update package index and install needed language packs
            argostranslate.package.update_package_index()
            available = argostranslate.package.get_available_packages()

            # Install hi->en, ta->en, bn->en if available
            target_langs = [("hi", "en"), ("ta", "en"), ("bn", "en")]
            for from_code, to_code in target_langs:
                pkg = next((p for p in available if p.from_code == from_code and p.to_code == to_code), None)
                if pkg:
                    logger.info("Installing translation pack: %s -> %s", from_code, to_code)
                    pkg.download().install()

            # Cache installed translators
            installed = argostranslate.translate.get_installed_languages()
            for lang in installed:
                for target in installed:
                    if lang.code != target.code:
                        self._translators[(lang.code, target.code)] = lang.get_translation(target)

            self._initialized = True
            logger.info("Offline translator initialized with %d language pairs", len(self._translators))
        except Exception as e:
            logger.warning("Offline translator init failed: %s", e)
            self._initialized = True  # Don't retry

    def translate(self, text: str, target: str = "en") -> str:
        if not text or target == "en" or detect_lang(text) == target:
            return text

        self._init_translators()

        source_lang = detect_lang(text)
        key = (source_lang, target)

        if key in self._translators:
            try:
                result = self._translators[key].translate(text)
                return str(result)
            except Exception as e:
                logger.warning("Translation failed for %s->%s: %s", source_lang, target, e)

        return text  # Fallback to original


# Global instance
_translator = OfflineTranslator()


def translate(text: str, target: str = "en") -> str:
    """Translate text to target language using offline translation."""
    return _translator.translate(text, target)
