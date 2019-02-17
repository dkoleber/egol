import numpy as np
cimport numpy as np
import time


WIDTH = 200
HEIGHT = 200


class World:
    def __init__(self, width, height):
        pass
    def convert_to_image(self):
        img = np.zeros((HEIGHT,WIDTH,3),np.uint8)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                pass
        return img
    def step(self):
        pass