"""Extract an .mp3 audio track from each .mp4 in a folder."""
import os

from moviepy import VideoFileClip


class AudioExtractor:
    def extract_audio(self, video_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for video_file in os.listdir(video_folder):
            if not video_file.endswith(".mp4"):
                continue

            video_path = os.path.join(video_folder, video_file)
            out_name = os.path.splitext(video_file)[0] + ".mp3"
            out_path = os.path.join(output_folder, out_name)

            clip = VideoFileClip(video_path)
            if clip.audio:
                clip.audio.write_audiofile(out_path)
            clip.close()
