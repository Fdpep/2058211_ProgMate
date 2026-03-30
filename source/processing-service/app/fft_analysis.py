import numpy as np


def extract_dominant_frequency(samples: list[float], sampling_rate_hz: float) -> float:
    if len(samples) < 2:
        return 0.0

    signal = np.array(samples, dtype=float)

    # Remove DC component
    signal = signal - np.mean(signal)

    # Apply Hann window 
    window = np.hanning(len(signal))
    signal = signal * window

    fft_result = np.fft.rfft(signal)
    magnitudes = np.abs(fft_result)
    frequencies = np.fft.rfftfreq(len(signal), d=1.0 / sampling_rate_hz)

    if len(magnitudes) <= 1:
        return 0.0

    # Remove DC bin
    magnitudes[0] = 0.0

    dominant_index = int(np.argmax(magnitudes))
    dominant_frequency = float(frequencies[dominant_index])

    return dominant_frequency


def extract_peak_amplitude(samples: list[float]) -> float:
    if not samples:
        return 0.0

    return float(max(abs(value) for value in samples))