"""Sample keyframes from each .mp4 at a fixed frames-per-second rate.

Frames are written as <HH-MM-SS>_<index>.jpg so the timestamp can later be
recovered from the filename during retrieval.
"""
import os
from collections import defaultdict
from datetime import timedelta

import cv2


class FrameExtractor:
    def __init__(self, frame_rate=2):
        self.frame_rate = frame_rate

    def extract_frames(self, video_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        for video_file in os.listdir(video_folder):
            if not video_file.endswith(".mp4"):
                continue

            video_path = os.path.join(video_folder, video_file)
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            step = max(1, int(fps // self.frame_rate))

            subfolder = os.path.join(output_folder, os.path.splitext(video_file)[0])
            os.makedirs(subfolder, exist_ok=True)

            per_second = defaultdict(int)
            success, image = cap.read()
            frame_number = 0
            while success:
                if frame_number % step == 0:
                    seconds = int(frame_number / fps)
                    ts = str(timedelta(seconds=seconds)).replace(":", "-")
                    per_second[ts] += 1
                    out = os.path.join(subfolder, f"{ts}_{per_second[ts]}.jpg")
                    cv2.imwrite(out, image)
                success, image = cap.read()
                frame_number += 1

            cap.release()
