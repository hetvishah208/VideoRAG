"""Transcribe extracted audio to plain-text transcripts using faster-whisper."""
import os

from faster_whisper import WhisperModel


class AudioTranscriber:
    def __init__(self, model_name="base", device="cpu", compute_type="int8"):
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)

    def transcribe(self, audio_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for file in os.listdir(audio_folder):
            if not file.endswith(".mp3"):
                continue

            audio_path = os.path.join(audio_folder, file)
            segments, _ = self.model.transcribe(audio_path)
            transcript_text = " ".join(seg.text.strip() for seg in segments)

            out_name = file.replace(".mp3", "_plain.txt")
            out_path = os.path.join(output_folder, out_name)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
