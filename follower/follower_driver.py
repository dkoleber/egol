import threading
from pyximport import pyximport
import subprocess
import os.path
import time
import cv2
import numpy as np
pyximport.install(language_level=3,setup_args={"include_dirs":np.get_include()})
# if os.path.exists('engine.c'):
#     os.remove('engine.c')
# subprocess.call(['cython','-3','follower_engine.pyx',])
import follower_engine as engine
from follower_engine import World,Actor



class Renderer(threading.Thread):
    def __init__(self,world : World, frames_per_sec : int):
        super(Renderer,self).__init__()
        self.world = world
        self.frame_time = int((1. / float(frames_per_sec)) * 1000)
    def run(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 300, 300)
        while True:
            cv2.imshow('image', self.world.convert_to_image())
            cv2.waitKey(self.frame_time)


if __name__ == '__main__':
    frames_per_sec = 30
    test_world = World(100,100)
    render = Renderer(test_world, frames_per_sec)
    render.start()

    # text_background = np.zeros((200,200,3), np.uint8)
    # cv2.putText()


    # for x in range(POPULATION_SIZE):
    #     test_world.add_actor(np.random.randint(test_world.width), np.random.randint(test_world.height), GroupMover(RADIUS, class_id=GROUPMOVER_CLASS_ID))
    stop_time = .001
    while True:
         start = time.time()
         test_world.step_world()
         duration = time.time() - start
         time.sleep(max(0,stop_time-duration))




    cv2.waitKey(0)
    cv2.destroyAllWindows()