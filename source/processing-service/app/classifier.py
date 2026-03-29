#Applicazione delle soglie
def classify_event(dominant_frequency_hz: float) -> str | None:
    if 0.5 <= dominant_frequency_hz < 3.0:
        return "earthquake"

    if 3.0 <= dominant_frequency_hz < 8.0:
        return "conventional_explosion"

    if dominant_frequency_hz >= 8.0:
        return "nuclear_like_event"

    return None