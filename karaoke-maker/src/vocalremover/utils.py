import os
import librosa
import numpy as np


def crop_center(h1, h2):
    h1_shape = h1.size()
    h2_shape = h2.size()

    if h1_shape[3] == h2_shape[3]:
        return h1
    elif h1_shape[3] < h2_shape[3]:
        raise ValueError("h1_shape[3] must be greater than h2_shape[3]")

    # s_freq = (h2_shape[2] - h1_shape[2]) // 2
    # e_freq = s_freq + h1_shape[2]
    s_time = (h1_shape[3] - h2_shape[3]) // 2
    e_time = s_time + h2_shape[3]
    h1 = h1[:, :, :, s_time:e_time]

    return h1


def wave_to_spectrogram(wave, hop_length, n_fft):
    wave_left = np.asfortranarray(wave[0])  # type:ignore
    wave_right = np.asfortranarray(wave[1])  # type:ignore

    spec_left = librosa.stft(wave_left, n_fft, hop_length=hop_length)
    spec_right = librosa.stft(wave_right, n_fft, hop_length=hop_length)
    spec = np.asfortranarray([spec_left, spec_right])  # type:ignore

    return spec


def spectrogram_to_image(spec, mode="magnitude"):
    if mode == "magnitude":
        if np.iscomplexobj(spec):
            y = np.abs(spec)
        else:
            y = spec
        y = np.log10(y**2 + 1e-8)  # type:ignore
    elif mode == "phase":
        if np.iscomplexobj(spec):
            y = np.angle(spec)
        else:
            y = spec

    y -= y.min()  # type:ignore
    y *= 255 / y.max()
    img = np.uint8(y)  # type:ignore

    if y.ndim == 3:
        img = img.transpose(1, 2, 0)  # type:ignore
        img = np.concatenate([np.max(img, axis=2, keepdims=True), img], axis=2)

    return img


def aggressively_remove_vocal(X, y, weight):
    X_mag = np.abs(X)
    y_mag = np.abs(y)
    # v_mag = np.abs(X_mag - y_mag)
    v_mag = X_mag - y_mag
    v_mag *= v_mag > y_mag

    y_mag = np.clip(y_mag - v_mag * weight, 0, np.inf)

    return y_mag * np.exp(1.0j * np.angle(y))  # type:ignore


def merge_artifacts(y_mask, thres=0.05, min_range=64, fade_size=32):
    if min_range < fade_size * 2:
        raise ValueError("min_range must be >= fade_size * 2")

    idx = np.where(y_mask.min(axis=(0, 1)) > thres)[0]
    start_idx = np.insert(idx[np.where(np.diff(idx) != 1)[0] + 1], 0, idx[0])
    end_idx = np.append(idx[np.where(np.diff(idx) != 1)[0]], idx[-1])
    artifact_idx = np.where(end_idx - start_idx > min_range)[0]
    weight = np.zeros_like(y_mask)
    if len(artifact_idx) > 0:
        start_idx = start_idx[artifact_idx]
        end_idx = end_idx[artifact_idx]
        old_e = None
        for s, e in zip(start_idx, end_idx):
            if old_e is not None and s - old_e < fade_size:
                s = old_e - fade_size * 2

            if s != 0:
                weight[:, :, s : s + fade_size] = np.linspace(
                    0, 1, fade_size
                )  # type:ignore
            else:
                s -= fade_size

            if e != y_mask.shape[2]:
                weight[:, :, e - fade_size : e] = np.linspace(
                    1, 0, fade_size
                )  # type:ignore
            else:
                e += fade_size

            weight[:, :, s + fade_size : e - fade_size] = 1  # type:ignore
            old_e = e

    v_mask = 1 - y_mask
    y_mask += weight * v_mask

    return y_mask


def align_wave_head_and_tail(a, b, sr):
    a, _ = librosa.effects.trim(a)
    b, _ = librosa.effects.trim(b)

    a_mono = a[:, : sr * 4].sum(axis=0)
    b_mono = b[:, : sr * 4].sum(axis=0)

    a_mono -= a_mono.mean()
    b_mono -= b_mono.mean()

    offset = len(a_mono) - 1
    delay = np.argmax(np.correlate(a_mono, b_mono, "full")) - offset

    if delay > 0:
        a = a[:, delay:]
    else:
        b = b[:, np.abs(delay) :]

    if a.shape[1] < b.shape[1]:
        b = b[:, : a.shape[1]]
    else:
        a = a[:, : b.shape[1]]

    return a, b


def cache_or_load(mix_path, inst_path, sr, hop_length, n_fft):
    mix_basename = os.path.splitext(os.path.basename(mix_path))[0]
    inst_basename = os.path.splitext(os.path.basename(inst_path))[0]

    cache_dir = "sr{}_hl{}_nf{}".format(sr, hop_length, n_fft)
    mix_cache_dir = os.path.join(os.path.dirname(mix_path), cache_dir)
    inst_cache_dir = os.path.join(os.path.dirname(inst_path), cache_dir)
    os.makedirs(mix_cache_dir, exist_ok=True)
    os.makedirs(inst_cache_dir, exist_ok=True)

    mix_cache_path = os.path.join(mix_cache_dir, mix_basename + ".npy")
    inst_cache_path = os.path.join(inst_cache_dir, inst_basename + ".npy")

    if os.path.exists(mix_cache_path) and os.path.exists(inst_cache_path):
        X = np.load(mix_cache_path)
        y = np.load(inst_cache_path)
    else:
        X, _ = librosa.load(
            mix_path, sr, False, dtype=np.float32, res_type="kaiser_fast"
        )
        y, _ = librosa.load(
            inst_path, sr, False, dtype=np.float32, res_type="kaiser_fast"
        )

        X, y = align_wave_head_and_tail(X, y, sr)

        X = wave_to_spectrogram(X, hop_length, n_fft)
        y = wave_to_spectrogram(y, hop_length, n_fft)

        np.save(mix_cache_path, X)
        np.save(inst_cache_path, y)

    return X, y, mix_cache_path, inst_cache_path


def spectrogram_to_wave(spec, hop_length=1024):
    if spec.ndim == 2:
        wave = librosa.istft(spec, hop_length=hop_length)
    elif spec.ndim == 3:
        spec_left = np.asfortranarray(spec[0])  # type:ignore
        spec_right = np.asfortranarray(spec[1])  # type:ignore

        wave_left = librosa.istft(spec_left, hop_length=hop_length)
        wave_right = librosa.istft(spec_right, hop_length=hop_length)
        wave = np.asfortranarray([wave_left, wave_right])  # type:ignore

    return wave  # type:ignore


def make_padding(width, cropsize, offset):
    left = offset
    roi_size = cropsize - offset * 2
    if roi_size == 0:
        roi_size = cropsize
    right = roi_size - (width % roi_size) + left

    return left, right, roi_size
