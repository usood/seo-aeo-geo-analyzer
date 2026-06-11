"""Small localization helpers for deterministic report UI labels."""

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_LANGUAGE = "en"
LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"


@dataclass(frozen=True)
class LocaleCatalog:
    """Translation catalog with English fallback."""

    language: str
    labels: dict
    fallback: dict

    def t(self, key: str) -> str:
        return self.labels.get(key) or self.fallback.get(key) or key


def _read_locale(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Locale file must contain an object: {path}")

    return {str(key): str(value) for key, value in data.items()}


def _normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE
    return str(language).strip().lower().split("_", 1)[0].split("-", 1)[0] or DEFAULT_LANGUAGE


def load_locale(language: str | None, locales_dir: Path | str = LOCALES_DIR) -> LocaleCatalog:
    """Load a locale merged over English fallback labels."""
    locales_dir = Path(locales_dir)
    fallback = _read_locale(locales_dir / f"{DEFAULT_LANGUAGE}.json")
    normalized = _normalize_language(language)
    locale_path = locales_dir / f"{normalized}.json"

    if normalized == DEFAULT_LANGUAGE or not locale_path.exists():
        return LocaleCatalog(language=DEFAULT_LANGUAGE, labels=fallback, fallback=fallback)

    labels = fallback | _read_locale(locale_path)
    return LocaleCatalog(language=normalized, labels=labels, fallback=fallback)


def resolve_report_language(config) -> str:
    """Resolve report language from report.language, then location.language_code."""
    return _normalize_language(
        config.get("report", "language", default=None)
        or config.get("location", "language_code", default=None)
    )


def find_unknown_locale_keys(locales_dir: Path | str = LOCALES_DIR) -> dict[str, list[str]]:
    """Return keys present in non-English locale files but absent from en.json."""
    locales_dir = Path(locales_dir)
    english_keys = set(_read_locale(locales_dir / f"{DEFAULT_LANGUAGE}.json"))
    unknown = {}

    for path in sorted(locales_dir.glob("*.json")):
        if path.name == f"{DEFAULT_LANGUAGE}.json":
            continue
        extra_keys = sorted(set(_read_locale(path)) - english_keys)
        if extra_keys:
            unknown[path.name] = extra_keys

    return unknown
