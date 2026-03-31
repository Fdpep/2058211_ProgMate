from app.config import MIN_CLASSIFIABLE_FREQUENCY_HZ


def classify_event(dominant_frequency_hz: float) -> str | None:
    if MIN_CLASSIFIABLE_FREQUENCY_HZ <= dominant_frequency_hz < 3.0:
        return "earthquake"

    if 3.0 <= dominant_frequency_hz < 8.0:
        return "conventional_explosion"

    if dominant_frequency_hz >= 8.0:
        return "nuclear_like"

    return None