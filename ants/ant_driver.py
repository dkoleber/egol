import threading
from pyximport import pyximport
import time
import cv2
import numpy as np
pyximport.install(language_level=3,setup_args={"include_dirs":np.get_include()})
import ant_engine as engine
from ant_engine import World


class Renderer(threading.Thread):
    def __init__(self,world : World, frames_per_sec : int):
        super(Renderer,self).__init__()
        self.world = world
        self.frame_time = int((1. / float(frames_per_sec)) * 1000)
        self.step_max = 1
    def run(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 500, 500)

        def on_rate_change(x):
            self.step_max = max(x,1)

        cv2.createTrackbar('steps max per second', 'image', 1, 400, on_rate_change)

        while True:
            cv2.imshow('image', self.world.convert_to_image())
            cv2.waitKey(self.frame_time)


if __name__ == '__main__':
    frames_per_sec = 30
    test_world = World(50,50)
    render = Renderer(test_world, frames_per_sec)
    render.start()

    stop_time = .001
    while True:
        start = time.time()
        test_world.step()
        duration = time.time() - start
        render.step_time = 1. / max(duration,0.001)
        stop_time = 1. / float(render.step_max)
        time.sleep(max(0, stop_time - duration))




    cv2.waitKey(0)
    cv2.destroyAllWindows()