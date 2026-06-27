import os
import re
from datetime import timedelta

def extract_frame_time_from_filename(filename):
    """
    Extract timestamp in seconds from frame filenames like '00-05-03_1.jpg'.
    Assumes filename format is HH-MM-SS_index.jpg.
    """
    try:
        base = os.path.splitext(os.path.basename(filename))[0]
        match = re.match(r"(\d+)-(\d+)-(\d+)_\d+", base)
        if match:
            h, m, s = map(int, match.groups())
            return timedelta(hours=h, minutes=m, seconds=s).total_seconds()
    except Exception as e:
        print(f"⚠️ Failed to parse timestamp from {filename}: {e}")
    return 0.0