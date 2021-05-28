import cv2
import sys

from datetime import datetime
from threading import Thread

import jetson.utils

class CountsPerSec:

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = datetime.now()
        return self

    def increment(self):
        self._num_occurrences += 1

    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        return self._num_occurrences / elapsed_time if elapsed_time > 0 else 0


class VideoGet:

    def __init__(self, uri="csi://0", input_codec="mjpeg", input_width="1920", input_height="1080"):
        self.stream = jetson.utils.videoSource(
            uri,
            argv= [
                f"--input_codec={input_codec}",
                f"--input_width={input_width}",
                f"--input_height={input_height}",
            ]
        )
        self.frame = self.stream.Capture()
        self.stopped = False

    def start(self):
        self.thread = Thread(target=self.get, args=())
        self.thread.start()
        return self

    def get(self):
        # TODO try - except con un release() al final del except antes de un printTraceback
        while not self.stopped:
            # if not self.grabbed:
            #     self.stop()
            # else:
            #     self.grabbed, self.frame = self.stream.read()
            #     self.frame = self.stream.Capture()
            self.frame = self.stream.Capture()

    def read(self):
        return self.frame
        # return self.frame.copy() ??

    def stop(self):
        self.stopped = True

    def release(self):
        self.stop()
        if self.thread != None:
            self.thread.join()
        self.stream.Close()


def putIterationsPerSec(frame, iterations_per_sec):
    cv2.putText(
        frame,
        "{:.0f} iterations/sec".format(iterations_per_sec),
        (10, 450),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255)
    )
    return frame


def main1():

    cam0 = VideoGet(0).start()
    cps = CountsPerSec().start()

    while True:

        frame_0 = cam0.read()
        jetson.utils.cudaDeviceSynchronize() # NECESARIO CHECK
        frame_0_cv2 = jetson.utils.cudaToNumpy(frame_0)
        frame_0_cv2_BGR = cv2.cvtColor(frame_0_cv2, cv2.COLOR_RGBA2BGR)
        frame_0_cv2_BGR = putIterationsPerSec(frame_0_cv2_BGR, cps.countsPerSec())
        cv2.imshow("Video0", frame_0_cv2_BGR)
        cps.increment()

        if cv2.waitKey(1) == ord("q") or cam0.stopped:
            cam0.release()
            cv2.destroyAllWindows()
            break


def main2():

    cam0 = VideoGet(0).start()
    cam1 = VideoGet(1).start()
    cps = CountsPerSec().start()

    while True:

        frame_0 = cam0.read()
        frame_1 = cam1.read()
        jetson.utils.cudaDeviceSynchronize() # NECESARIO CHECK
        frame_0_cv2 = jetson.utils.cudaToNumpy(frame_0)
        frame_1_cv2 = jetson.utils.cudaToNumpy(frame_1)
        frame_0_cv2_BGR = cv2.cvtColor(frame_0_cv2, cv2.COLOR_RGBA2BGR)
        frame_1_cv2_BGR = cv2.cvtColor(frame_1_cv2, cv2.COLOR_RGBA2BGR)
        frame_0_cv2_BGR = putIterationsPerSec(frame_0_cv2_BGR, cps.countsPerSec())
        frame_1_cv2_BGR = putIterationsPerSec(frame_1_cv2_BGR, cps.countsPerSec())
        cv2.imshow("Video0", frame_0_cv2_BGR)
        cv2.imshow("Video1", frame_1_cv2_BGR)
        cps.increment()

        if cv2.waitKey(1) == ord("q") or cam0.stopped or cam1.stopped:
            cam0.release()
            cam1.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main1()
    # main2()