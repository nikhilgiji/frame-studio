"""Create the tiny deterministic video used by browser tests."""

from pathlib import Path

import cv2
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "frontend" / "tests" / "fixtures" / "e2e.avi"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
writer = cv2.VideoWriter(str(OUTPUT), cv2.VideoWriter_fourcc(*"MJPG"), 10, (96, 64))
if not writer.isOpened():
    raise RuntimeError("Could not create the Playwright video fixture.")
for index in range(30):
    frame = np.zeros((64, 96, 3), dtype=np.uint8)
    frame[:, :, 0] = index * 7
    cv2.putText(frame, str(index), (25, 42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    writer.write(frame)
writer.release()
