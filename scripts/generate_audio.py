"""Filter the original film effects; never synthesize replacement sounds.

Requires FFmpeg, NumPy and SciPy to rebuild. Playback only requires pygame.
"""
from pathlib import Path
import subprocess
import wave

import numpy as np
from scipy.ndimage import median_filter, gaussian_filter
from scipy.signal import stft, istft

ROOT = Path(__file__).resolve().parents[1]
RATE = 44100


def generate():
    command = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(ROOT / 'easymoney.mp4'),
        '-filter_complex',
        '[0:a]atrim=start=2.45:end=4.45,asetpts=PTS-STARTPTS[a];'
        '[0:a]atrim=start=6:end=9,asetpts=PTS-STARTPTS[b];'
        '[a][b]concat=n=2:v=0:a=1[out]',
        '-map', '[out]', '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1',
    ]
    raw = subprocess.run(command, check=True, capture_output=True).stdout
    original = np.frombuffer(raw, dtype='<f4').reshape(-1, 2)
    f, t, spectrum = stft(original, RATE, nperseg=2048, noverlap=1536, axis=0)
    left, right = spectrum[:, 0, :], spectrum[:, 1, :]
    mid, side = (left + right) / 2, (left - right) / 2
    # Dialogue is predominantly in the center; retain the original stereo effects.
    # Remove low speech harmonics, then retain narrow electronic peaks in center.
    magnitude = abs(mid)
    local_floor = median_filter(magnitude, size=(21, 1))
    peak_mask = np.clip((magnitude / (local_floor + 1e-9) - 2) / 4, 0, 1)
    peak_mask = gaussian_filter(peak_mask, sigma=(.6, .6))
    highpass = np.clip((f - 1700) / 700, 0, 1)[:, None] ** 2
    clean_mid = mid * peak_mask * highpass
    clean_side = side * highpass
    channels = []
    for filtered in (clean_mid + clean_side, clean_mid - clean_side):
        _, signal = istft(filtered, RATE, nperseg=2048, noverlap=1536)
        channels.append(signal[:len(original)])
    clean = np.column_stack(channels)
    # Preserve the original dynamics; only compensate the loss from separation.
    peak = np.max(abs(clean))
    if peak:
        clean *= min(3, .75 / peak)
    fade = int(.015 * RATE)
    clean[:fade] *= np.linspace(0, 1, fade)[:, None]
    clean[-fade:] *= np.linspace(1, 0, fade)[:, None]
    target = ROOT / 'assets' / 'identification.wav'
    with wave.open(str(target), 'wb') as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes((np.clip(clean, -1, 1) * 32767).astype('<i2').tobytes())
    print('Original audio filtered: stereo dialogue suppression and spectral filtering.')


if __name__ == '__main__':
    generate()
