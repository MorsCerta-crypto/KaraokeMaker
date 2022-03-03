import os

import librosa
import numpy as np
import soundfile as sf
import torch
import tqdm
from src.vocalremover import nets, utils


class VocalRemover:
    def __init__(self,config:dict):
        device = torch.device("cpu")
        self.model = nets.CascadedNet(config["n_fft"])  # type:ignore
        self.model.load_state_dict(torch.load(config["pretrained_model"], map_location=device))
        if torch.cuda.is_available():  # type:ignore
            device = torch.device("cuda:0")
            self.model.to(device)

        self.offset = self.model.offset
        self.device = device
        
        self.batchsize = config["batchsize"]
        self.cropsize = config["cropsize"]
        self.postprocess = config["postprocess"]
        self.hop_length = config["hop_length"]
        self.n_fft = config["n_fft"]
        self.tta = config["tta"]
        self.sample_rate = config["sample_rate"]
        export_folder = config["export_folder"]
                                  
        if not export_folder.endswith("/"):
            export_folder = export_folder + "/"
        self.instrumentals_folder = export_folder + "backing_tracks/"
        self.vocals_folder = export_folder + "voices/"

        # create directories if necessary
        if not os.path.exists(self.instrumentals_folder):
            os.makedirs(self.instrumentals_folder)
        if not os.path.exists(self.vocals_folder):
            os.makedirs(self.vocals_folder)

    def remove_vocals(self, file: str):
        """remove_vocals from a given file"""  #

        if not file.split(".")[1] in ["mp3", "wav"]:
            raise ValueError("file ending not supported")
        X, sample_rate = librosa.load(
            file, sr=self.sample_rate, mono=False, dtype=np.float32, res_type="kaiser_fast"
        )
        basename = os.path.splitext(os.path.basename(file))[0]

        if X.ndim == 1:  # type:ignore
            # mono to stereo
            X = np.asarray([X, X])  # type:ignore

        X_spec = utils.wave_to_spectrogram(X, self.hop_length, self.n_fft)

        y_spec, v_spec = self.separate(X_spec)

        # nverse stft of instruments
        wave = utils.spectrogram_to_wave(y_spec, hop_length=self.hop_length)
        sf.write(
            f"{self.instrumentals_folder}{basename}_Instruments.wav",
            wave.T,  # type:ignore
            sample_rate,
        )

        # inverse stft of vocals
        wave = utils.spectrogram_to_wave(v_spec, hop_length=self.hop_length)
        sf.write(f"{self.vocals_folder}{basename}_Vocals.wav", wave.T, sample_rate)  # type:ignore

    def _separate(self, X_mag_pad, roi_size):
        X_dataset = []
        patches = (X_mag_pad.shape[2] - 2 * self.offset) // roi_size
        for i in range(patches):
            start = i * roi_size
            X_mag_crop = X_mag_pad[:, :, start : start + self.cropsize]
            X_dataset.append(X_mag_crop)

        X_dataset = np.asarray(X_dataset)  # type:ignore

        self.model.eval()
        with torch.no_grad():
            mask = []
            # To reduce the overhead, dataloader is not used.
            for i in tqdm.tqdm(range(0, patches, self.batchsize)):
                X_batch = X_dataset[i : i + self.batchsize]  # type:ignore
                X_batch = torch.from_numpy(X_batch).to(self.device)

                pred = self.model.predict_mask(X_batch)

                pred = pred.detach().cpu().numpy()  # type:ignore
                pred = np.concatenate(pred, axis=2)
                mask.append(pred)

            mask = np.concatenate(mask, axis=2)

        return mask

    def _preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def _postprocess(self, mask, X_mag, X_phase):
        if self.postprocess:
            mask = utils.merge_artifacts(mask)

        y_spec = mask * X_mag * np.exp(1.0j * X_phase)  # type:ignore
        v_spec = (1 - mask) * X_mag * np.exp(1.0j * X_phase)  # type:ignore

        return y_spec, v_spec

    def separate(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = utils.make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)
        if self.tta:
            pad_l += roi_size // 2
            pad_r += roi_size // 2
            X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")
            X_mag_pad /= X_mag_pad.max()

            mask_tta = self._separate(X_mag_pad, roi_size)
            mask_tta = mask_tta[:, :, roi_size // 2 :]  # type:ignore
            mask = (
                mask[:, :, :n_frame] + mask_tta[:, :, :n_frame]  # type:ignore
            ) * 0.5
        else:
            mask = mask[:, :, :n_frame]  # type:ignore

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec


if __name__ == "__main__":
    i = VocalRemover()
    i.remove_vocals(file="")
