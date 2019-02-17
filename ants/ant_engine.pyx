import numpy as np
cimport numpy as np
import time

RESIZE_BY = 25

pixel_values = [(255,255,255),(255,0,0),(0,255,0),(0,0,255)]
switches_to = [1,2,0]
bearings = [-90,90,90]




class World:
    def __init__(self, width, height, config = 2):
        self.width = width
        self.height = height
        self.grid = np.zeros((width,height),np.uint8)
        self.ant_x = int(width/2)
        self.ant_y = int(height/2)
        self.bearing = 90.
        self.stage = 0
        self.rendering = np.full((width,height,3),255, np.uint8)
        load_config(config)
    def convert_to_image(self):
        return self.rendering
    def step(self):
        #start_time = time.time()
        self.resize_grid()
        current = self.grid[self.ant_x,self.ant_y]
        self.bearing += bearings[current]
        self.bearing %= 360
        [delta_x, delta_y] = np.around([np.cos(np.pi * self.bearing / 180.), np.sin(np.pi * self.bearing / 180.)])
        delta_x = int(delta_x)
        delta_y = int(delta_y)
        #print('stage: ' + str(self.stage) + ' | bearing: ' + str(self.bearing) + ' | delta: ' + str(delta_x) + ', ' + str(delta_y) + ' | next: ' + str(switches_to[self.stage]))
        self.grid[self.ant_x, self.ant_y] = switches_to[current]
        self.rendering[self.ant_x, self.ant_y] = pixel_values[switches_to[current]]
        self.ant_x += delta_x
        self.ant_y += delta_y
        self.rendering[self.ant_x, self.ant_y] = (0, 0, 0)
        #print('step: ' + str(time.time() - start_time))
    def resize_grid(self):
        needs_width_resize_start = self.ant_x == 0
        needs_width_resize_end = self.ant_x == self.width - 1
        needs_height_resize_start = self.ant_y == 0
        needs_height_resize_end = self.ant_y == self.height - 1

        if needs_width_resize_start or needs_width_resize_end or needs_height_resize_start or needs_height_resize_end:
            new_width = self.width
            new_height = self.height

            new_width += RESIZE_BY if needs_width_resize_start else 0
            new_width += RESIZE_BY if needs_width_resize_end else 0
            new_height += RESIZE_BY if needs_height_resize_start else 0
            new_height += RESIZE_BY if needs_height_resize_end else 0

            start_x = RESIZE_BY if needs_width_resize_start else 0
            start_y = RESIZE_BY if needs_height_resize_start else 0

            new_grid = np.zeros((new_width,new_height),np.uint8)
            new_grid[start_x:start_x+self.width,start_y:start_y+self.height] = self.grid
            new_rendering = np.full((new_width,new_height,3),255,np.uint8)
            new_rendering[start_x:start_x+self.width,start_y:start_y+self.height,:] = self.rendering

            self.grid = new_grid
            self.rendering = new_rendering
            self.width = new_width
            self.height = new_height
            self.ant_x += RESIZE_BY if needs_width_resize_start else 0
            self.ant_y += RESIZE_BY if needs_height_resize_start else 0

def load_config(config):
    switch = [config_default, config_waller, config_3, config_4, config_5]
    switch[config]()

def config_default():
    global switches_to
    global bearings
    switches_to = [1,0]
    bearings = [-90,90]

def config_waller():
    global switches_to
    global bearings
    switches_to = [1,2,0]
    bearings = [-90,90,90]

def config_3():
    global switches_to
    global bearings
    switches_to = [1,2,3,0]
    bearings = [-90,90,90,-90]

def config_4():
    global switches_to
    global bearings

def config_5():
    global switches_to
    global bearings




