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
# subprocess.call(['cython','-3','engine.pyx',])
import engine2
from engine2 import Grid
#print(engine.do_something(1))

start_pos = 0
nutrient_scale = 0
oxygen_scale = 0
energy_scale = 0


class Renderer(threading.Thread):
    def __init__(self,grid : Grid, frames_per_sec : int):
        super(Renderer,self).__init__()
        self.grid = grid
        self.frame_time = (1. / float(frames_per_sec)) * 1000.
        self.step_time = 0
        self.x = -1
        self.y = -1
        self.steps = 0

        self.step_max = 1
    def run(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 500, 500)

        cv2.namedWindow('info', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('info', 500, 500)

        def mouseHandler(event, x, y, flags, param):
            self.x = x
            self.y = y
        cv2.setMouseCallback('image', mouseHandler)


        def on_nutrient_change(x):
            global nutrient_scale
            nutrient_scale = x
        def on_oxygen_change(x):
            global oxygen_scale
            oxygen_scale = x
        def on_energy_change(x):
            global energy_scale
            energy_scale = x
        def on_rate_change(x):
            self.step_max = max(x,1)

        cv2.createTrackbar('nutrients on plant','image',0,100,on_nutrient_change)
        cv2.createTrackbar('oxygen on plant','image',0,100,on_oxygen_change)
        cv2.createTrackbar('energy on plant','image',0,100,on_energy_change)
        cv2.createTrackbar('steps max per second', 'image',1, 100,on_rate_change)



        global nutrient_scale
        global oxygen_scale
        global energy_scale
        global start_pos

        while True:

            duration = time.time()
            image = self.grid.convert_to_image(nutrient_scale, oxygen_scale, energy_scale)
            cv2.imshow('image', image)


            start_pos = 13
            def next_pos():
                global start_pos
                start_pos += 20
                return start_pos

            info_image = np.zeros((500,500,3))
            cv2.putText(info_image, 'steps per second: ' + str(self.step_time)[:5], (00, start_pos), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
            cv2.putText(info_image, 'steps: ' + str(self.steps), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
            if self.x >= 0 and self.y >= 0:
                cv2.putText(info_image, 'nutrients: ' + str(self.grid.grid[self.x,self.y,engine2.NUTRIENTS_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'oxygen: ' + str(self.grid.grid[self.x,self.y,engine2.OXYGEN_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'energy: ' + str(self.grid.grid[self.x,self.y,engine2.ENERGY_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'type: ' + engine2.get_type_string(self.grid.types[self.x,self.y]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )

            cv2.imshow('info', info_image)

            duration = time.time() - duration

            cv2.waitKey(int(max(self.frame_time-duration,0)))


if __name__ == '__main__':
    frames_per_sec = 30
    test_world = Grid()
    render = Renderer(test_world, frames_per_sec)
    render.start()
    while True:
         start = time.time()
         test_world.step()
         duration = time.time() - start
         render.step_time = 1./duration

         stop_time = 1. / float(render.step_max)

         time.sleep(max(0,stop_time-duration))
         render.steps += 1




    cv2.waitKey(0)
    cv2.destroyAllWindows()