import numpy as np
cimport numpy as np
import time

RESIZE_BY = 25

class World:
    def __init__(self, width, height, config = 2):
        self.pixel_values = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.switches_to = [1, 2, 0]
        self.bearings = [-90, 90, 90]

        self.width = width
        self.height = height
        self.grid = np.zeros((width,height),np.uint8)

        self.ant_x = int(width/2)
        self.ant_y = int(height/2)
        self.bearing = 90.

        self.rendering = np.full((width,height,3),255, np.uint8)

        self.world_mode = config
        self.load_config()

    def convert_to_image(self):
        return self.rendering

    def step(self):
        #start_time = time.time()
        self.resize_grid()
        current = self.grid[self.ant_x,self.ant_y]
        self.bearing += self.bearings[current]
        self.bearing %= 360
        [delta_x, delta_y] = np.around([np.cos(np.pi * self.bearing / 180.), np.sin(np.pi * self.bearing / 180.)])
        delta_x = int(delta_x)
        delta_y = int(delta_y)
        #print('stage: ' + str(self.stage) + ' | bearing: ' + str(self.bearing) + ' | delta: ' + str(delta_x) + ', ' + str(delta_y) + ' | next: ' + str(switches_to[self.stage]))
        self.grid[self.ant_x, self.ant_y] = self.switches_to[current]
        self.rendering[self.ant_x, self.ant_y] = self.pixel_values[self.switches_to[current]]
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

    def load_config(self):
        switch = [self.config_default, self.config_waller, self.config_3, self.config_4, self.config_5]
        switch[self.world_mode]()

    def config_default(self):
        self.switches_to = [1,0]
        self.bearings = [-90,90]
        self.pixel_values = [(255, 255, 255), (255, 0, 0)]

    def config_waller(self):
        self.switches_to = [1,2,0]
        self.bearings = [-90,90,90]
        self.pixel_values = [(255, 255, 255), (255, 0, 0), (0, 255, 0)]

    def config_3(self):
        self.switches_to = [1,2,3,0]
        self.bearings = [-90,90,90,-90]
        self.pixel_values = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]

    def config_4(self):
        self.switches_to = [1, 2, 3, 0]
        self.bearings = [-45, 90, 45, -90]
        self.pixel_values = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]

    def config_5(self):
        self.switches_to = [1, 2, 0]
        self.bearings = [-45, 90, -90]
        self.pixel_values = [(255, 255, 255), (255, 0, 0), (0, 255, 0)]

    def set_config(self, data):
        if 'switches_to' in data \
            and 'bearings' in data \
            and 'pixel_values' in data \
            and 'ant_x' in data \
            and 'ant_y' in data \
            and 'bearing' in data \
            and 'world_mode' in data \
            and len(data['switches_to']) == len(data['bearings']) \
            and len(data['bearings']) == len(data['pixel_values']):
            self.switches_to = data['switches_to']
            self.bearings = data['bearings']
            self.pixel_values = data['pixel_values']
            self.ant_x = data['ant_x']
            self.ant_y = data['ant_y']
            self.bearing = data['bearing']
            self.world_mode = data['world_mode']
            self.load_config()
        else:
            self.config_default()

    def get_config(self):
        return {'switches_to' : self.switches_to,
                'bearings' : self.bearings,
                'pixel_values' : self.pixel_values,
                'ant_x' : self.ant_x,
                'ant_y' : self.ant_y,
                'bearing' : self.bearing,
                'world_mode' : self.world_mode}

    def set_grid(self, img):
        self.rendering = img
        self.width = img.shape[0]
        self.height = img.shape[1]
        self.grid = np.zeros((self.width, self.height), np.uint8)
        try:
            for x in range(self.width):
                for y in range(self.height):
                    pixel = img[x, y]
                    tile = 0
                    found = False
                    for z in range(len(self.pixel_values)):
                        if same(self.pixel_values[z],pixel):
                            tile = z
                            found = True
                    if not found:
                        print('not found: ', pixel)
                    self.grid[x,y] = tile
        except Exception as e:
            print(e)
        self.rendering[self.ant_x, self.ant_y] = (0, 0, 0)

    def get_grid(self):
        img = np.zeros((self.width,self.height,3), np.uint8)
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                img[x,y] = self.pixel_values[self.grid[x,y]]
        return img

def same(pixel_1, pixel_2):
    return pixel_1[0] == pixel_2[0] and pixel_1[1] == pixel_2[1] and pixel_1[2] == pixel_2[2]
