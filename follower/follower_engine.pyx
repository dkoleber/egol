import numpy as np
cimport numpy as np
import time

def do_something(num):
    return num+1


DEFAULT_INNER_RADIUS = 5.
DEFAULT_OUTER_RADIUS = 10.
DEFAULT_MOMENTUM = 0.
DEFAULT_VELOCITY = 1.

VELOCITY_CAP = 5.

NEW_WEIGHT = .75

DEFAULT_POPULATION = 30

WALL_PUSH = DEFAULT_POPULATION

def rand_int(max):
    return np.random.randint(max)

def rand_float(max):
    return np.random.random_sample() * max

def bound(val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

class Actor:
    def __init__(self, x, y, angle, velocity = DEFAULT_VELOCITY, momentum = DEFAULT_MOMENTUM, inner_radius = DEFAULT_INNER_RADIUS, outer_radius = DEFAULT_OUTER_RADIUS):
        self.x = x
        self.y = y
        self.angle = angle
        self.velocity = velocity
        self.momentum = momentum
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius

    def get_next_position(self, delta_x, delta_y, max_x, max_y):
        new_angle = np.arctan2(delta_y, delta_x)* NEW_WEIGHT  + self.angle * (1-NEW_WEIGHT)
        delta_xv = np.cos(new_angle) * self.velocity
        delta_yv = np.sin(new_angle) * self.velocity
        return bound(self.x + delta_xv, 0, max_x), bound(self.y + delta_yv, 0, max_y), new_angle

    def distance_to(self,other):
        return np.sqrt(np.power(self.x - other.x,2) + np.power(self.y - other.y,2))
    def in_outer(self,other):
        return self.distance_to(other) < self.outer_radius
    def in_inner(self,other):
        return self.distance_to(other) < self.inner_radius
class World:
    def __init__(self, width, height, population : int = DEFAULT_POPULATION):
        self.width = width
        self.height = height
        self.population = population
        self.actors = [Actor(rand_float(self.width),rand_float(self.height),rand_int(np.pi*2.)) for x in range(self.population)]

    def step_world(self):
        for actor in self.actors:
            pull_x, pull_y = actor.x, actor.y
            pull_counter = 0.
            push_x, push_y = actor.x, actor.y
            push_counter = 0.
            for other in self.actors:
                if actor != other and actor.in_outer(other):
                    if actor.in_inner(other):
                        push_x += other.x
                        push_y += other.y
                        push_counter += 1.
                    else:
                        pull_x += other.x
                        pull_y += other.y
                        pull_counter += 1.

            pull_x /= max(pull_counter,1.)
            pull_y /= max(pull_counter,1.)
            push_x /= max(push_counter,1.)
            push_y /= max(push_counter,1.)

            delta_x = pull_x - push_x
            delta_y = pull_y - push_y

            if actor.x < actor.outer_radius:
                delta_x = DEFAULT_VELOCITY
            if actor.x > self.width - actor.outer_radius - 1.:
                delta_x = -DEFAULT_VELOCITY
            if actor.y < actor.outer_radius:
                delta_y = DEFAULT_VELOCITY
            if actor.y > self.height - actor.outer_radius - 1.:
                delta_y = -DEFAULT_VELOCITY

            actor.x, actor.y, actor.angle = actor.get_next_position(delta_x,delta_y, self.width-1, self.height-1)
    def convert_to_image(self):

        img = np.ndarray((self.width,self.height,3),np.uint8)
        img.fill(255)
        for actor in self.actors:
            img[int(actor.x),int(actor.y)] = (100,100,100)
        return img
        # out_grid = self.get_active_grid()
        # for x in range(0,self.width):
        #     for y in range(0,self.height):
        #         pos = out_grid.grid[x,y,0]
        #         if pos[GUID_POS] > 1:
        #             #actor = self.actors[guid]
        #             img[x, y] = (pos[GUID_POS] % 256,(pos[GUID_POS] + 85) % 256,(pos[GUID_POS] + 170) % 256) #np.random.randint(255,size=(3))