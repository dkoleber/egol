import threading
from pyximport import pyximport
import subprocess
import os.path
import time
import cv2
import numpy as np
pyximport.install(language_level=3,setup_args={"include_dirs":np.get_include()})
import tree_engine as engine
from tree_engine import Grid
from tree_stats import *

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

        self.running = True
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

        while self.running:
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
                cv2.putText(info_image, 'nutrients: ' + str(self.grid.grid[self.x,self.y,engine.NUTRIENTS_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'oxygen: ' + str(self.grid.grid[self.x,self.y,engine.OXYGEN_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'energy: ' + str(self.grid.grid[self.x,self.y,engine.ENERGY_INDEX]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )
                cv2.putText(info_image, 'type: ' + engine.get_type_string(self.grid.types[self.x,self.y]), (00, next_pos()), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), )

            cv2.imshow('info', info_image)

            duration = time.time() - duration
            cv2.waitKey(int(max(self.frame_time-duration,0)))

    def stop(self):
        self.running = False

RUN_BATCH = False
if __name__ == '__main__':
    if not RUN_BATCH:
        frames_per_sec = 30
        test_world = Grid()
        render = Renderer(test_world, frames_per_sec)
        render.start()
        sim_name = 'tree_' + str(time.time())
        #stats_manager = TreeStats(sim_name, test_world.get_config())
        print(sim_name)

        cont = True

        while cont:

            start = time.time()
            cont = test_world.step()
            duration = time.time() - start
            render.step_time = 1./duration

            stop_time = 1. / float(render.step_max)

            time.sleep(max(0,stop_time-duration))

            if render.steps % 10 == 0:
                stats = test_world.get_stats()
                #stats_manager.add_entry(render.steps, stats)
            render.steps += 1

        cv2.destroyAllWindows()
        render.stop()
        stats_manager.show_stats()
    else:
        def run_sim(config):
            test_world = Grid(config)
            sim_name = 'tree_' + str(time.time())
            stats_manager = TreeStats(sim_name, test_world.get_config())
            print(sim_name)
            cont = True
            steps = 0
            while cont:
                cont = test_world.step()
                if steps % 10 == 0:
                    stats = test_world.get_stats()
                    stats_manager.add_entry(steps, stats)
                steps += 1

        def update_config(config, property, value):
            config[property] = value
            return config

        base_world = Grid()
        base_config = base_world.default_config()

        SAMPLES = 1

        energy_decay = np.random.random_integers(1,5,SAMPLES)
        grow_threshold = np.random.random_integers(5,20,SAMPLES)
        x_for_energy = np.random.random_integers(1,5,SAMPLES)
        energy_from_photo = np.random.random_integers(10,80,SAMPLES)

        for x in range(SAMPLES):
            run_sim(update_config(base_world.default_config(),'energy_decay',energy_decay[x]))
            run_sim(update_config(base_world.default_config(),'grow_threshold',grow_threshold[x]))
            run_sim(update_config(base_world.default_config(),'energy_from_photo',energy_from_photo[x]))
            new_config = base_world.default_config()
            new_config['nutrients_for_energy'] = x_for_energy[x]
            new_config['oxygen_for_energy'] = x_for_energy[x]
            run_sim(new_config)