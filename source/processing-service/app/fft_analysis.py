import numpy as np


def _parabolic_interpolation(magnitudes: np.ndarray, peak_index: int) -> float:
    if peak_index <= 0 or peak_index >= len(magnitudes) - 1:
        return 0.0

    alpha = magnitudes[peak_index - 1]
    beta = magnitudes[peak_index]
    gamma = magnitudes[peak_index + 1]

    denominator = alpha - 2 * beta + gamma
    if denominator == 0:
        return 0.0

    return 0.5 * (alpha - gamma) / denominator


def _remove_linear_trend(signal: np.ndarray) -> np.ndarray:
    if len(signal) < 2:
        return signal.copy()

    x = np.arange(len(signal), dtype=float)
    coeffs = np.polyfit(x, signal, deg=1)
    trend = coeffs[0] * x + coeffs[1]
    return signal - trend


def _compute_spectrum(
    signal: np.ndarray,
    sampling_rate_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    if len(signal) < 2:
        return np.array([]), np.array([])

    window = np.hanning(len(signal))
    windowed = signal * window

    padded_length = max(len(signal) * 4, len(signal))
    fft_result = np.fft.rfft(windowed, n=padded_length)
    magnitudes = np.abs(fft_result)
    frequencies = np.fft.rfftfreq(padded_length, d=1.0 / sampling_rate_hz)

    if len(magnitudes) > 0:
        magnitudes[0] = 0.0

    return frequencies, magnitudes


def _estimate_peak_frequency_from_spectrum(
    frequencies: np.ndarray,
    magnitudes: np.ndarray,
    min_frequency_hz: float | None = None,
) -> tuple[float, float]:
    if len(frequencies) == 0 or len(magnitudes) == 0:
        return 0.0, 0.0

    if min_frequency_hz is not None:
        valid_indices = np.where(frequencies >= min_frequency_hz)[0]
        if len(valid_indices) == 0:
            return 0.0, 0.0

        valid_magnitudes = magnitudes[valid_indices]
        if np.all(valid_magnitudes == 0):
            return 0.0, 0.0

        local_peak_pos = int(np.argmax(valid_magnitudes))
        peak_index = int(valid_indices[local_peak_pos])
    else:
        if np.all(magnitudes == 0):
            return 0.0, 0.0
        peak_index = int(np.argmax(magnitudes))

    correction = _parabolic_interpolation(magnitudes, peak_index)
    bin_spacing = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 0.0
    refined_frequency = frequencies[peak_index] + correction * bin_spacing
    peak_magnitude = float(magnitudes[peak_index])

    return float(max(refined_frequency, 0.0)), peak_magnitude


def analyze_frequency_spectrum(
    samples: list[float],
    sampling_rate_hz: float,
    min_classifiable_frequency_hz: float = 0.5,
) -> dict:
    if len(samples) < 2:
        return {
            "overall_dominant_frequency_hz": 0.0,
            "classifiable_dominant_frequency_hz": 0.0,
            "signal_rms": 0.0,
            "classifiable_peak_magnitude": 0.0,
        }

    raw_signal = np.array(samples, dtype=float)

    # Remove mean and linear drift only
    raw_signal = raw_signal - np.mean(raw_signal)
    detrended_signal = _remove_linear_trend(raw_signal)

    signal_rms = float(np.sqrt(np.mean(detrended_signal ** 2))) if len(detrended_signal) else 0.0

    frequencies, magnitudes = _compute_spectrum(
        detrended_signal,
        sampling_rate_hz,
    )

    overall_dominant_frequency_hz, _ = _estimate_peak_frequency_from_spectrum(
        frequencies,
        magnitudes,
        min_frequency_hz=None,
    )

    classifiable_dominant_frequency_hz, classifiable_peak_magnitude = _estimate_peak_frequency_from_spectrum(
        frequencies,
        magnitudes,
        min_frequency_hz=min_classifiable_frequency_hz,
    )

    return {
        "overall_dominant_frequency_hz": overall_dominant_frequency_hz,
        "classifiable_dominant_frequency_hz": classifiable_dominant_frequency_hz,
        "signal_rms": signal_rms,
        "classifiable_peak_magnitude": classifiable_peak_magnitude,
    }


def extract_peak_amplitude(samples: list[float]) -> float:
    if not samples:
        return 0.0

    return float(max(abs(value) for value in samples))