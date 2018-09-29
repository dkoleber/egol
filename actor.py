import numpy as np
from enum import Enum
import cv2
import time
import threading
import uuid

GUID_POS = 0
CLASS_ID_POS = 1

CLASSES = []
NUM_CLASSES = len(CLASSES) + 2 # + 2 because empty space and wall
SPACES_PER_POSITION = 4
OPEN_SPACE_CLASS = 0
OPEN_SPACE_GUID = 0

class Action(Enum):
    LEFT = 0,
    UP = 1,
    RIGHT = 2,
    DOWN = 3,
    NONE = 4

class Actor:
    def __init__(self, complexity : int, visual_radius : int):
        self.complexity = complexity
        self.traits = {'visual_radius' : visual_radius}
    def get_normalized_traits(self) -> list:
        trait_sum = sum(self.traits.values())
        return [{k,int(x / trait_sum)} for (k,x) in self.traits] #intentionally cast into int, actor probably loses some total complexity due to this
    def get_action(self, visual_field : np.ndarray, actor_dict : dict) -> Action:
        return Action.NONE
    def get_move(delta_x : int, delta_y : int):
        if delta_x > 0 and abs(delta_x) > abs(delta_y): return Action.RIGHT
        if delta_x < 0 and abs(delta_x) > abs(delta_y): return Action.LEFT
        if delta_y > 0 and abs(delta_x) < abs(delta_y): return Action.DOWN
        if delta_y < 0 and abs(delta_x) < abs(delta_y): return Action.UP
        return Action.NONE


class RandomMover(Actor):
    def get_action(self, visual_field : np.ndarray, actor_dict : dict):
        switch = [Action.LEFT, Action.UP, Action.RIGHT, Action.DOWN, Action.NONE]
        return switch[np.random.randint(len(switch))]

class GroupMover(Actor):
    def get_action(self, visual_field : np.ndarray, actor_dict : dict):
        x_desire = 0 #TODO: complete this


class Grid:
    def __init__(self, width : int, height : int):
        self.width = width
        self.height = height
        self.grid = np.ndarray((width,height,SPACES_PER_POSITION,2),dtype=int)
        self.grid.fill(0)
    def mask_visual_field(self, x : int, y : int, radius):
        x_start = max(0,x-radius)
        x_end = min(x+radius,self.width)
        y_start = max(0,y-radius)
        y_end = min(y+radius,self.height)
        return self.grid[x_start:x_end,y_start:y_end,:,:]
    def new_position(x : int, y : int, move : Action) -> (int, int):
        new_x = x
        new_y = y
        if move == Action.UP: new_y -= 1
        if move == Action.DOWN: new_y += 1
        if move == Action.LEFT: new_x -= 1
        if move == Action.RIGHT: new_x += 1
        return (new_x, new_y)
    def can_make_move(self,x : int, y : int, move : Action) -> bool:
        if move == Action.UP and y == 0: return False
        if move == Action.DOWN and y == self.height - 1: return  False
        if move == Action.LEFT and x == 0: return False
        if move == Action.RIGHT and x == self.width - 1: return False
        return True
    def move_actor(self, x, y, actor_entry):#TODO: needs to be changed
        space = self.grid[x,y]
        self.grid[x,y,Grid.next_space(space)] = actor_entry
    def count_occurrences(grid : np.ndarray, class_id : int):
        delete_guid = np.delete(grid,0,axis=3)
        classes, counts = np.unique(delete_guid, return_counts=True)
        return dict(zip(classes,counts))[class_id]
    def next_space(space : np.ndarray):
        open_space = space == OPEN_SPACE_GUID
        return np.argmax(np.argmin(open_space,axis=1))

class World:
    def __init__(self, width : int, height : int):
        self.width = width
        self.height = height
        self.grid_1 = Grid(width,height) #grids of GUID
        self.grid_2 = Grid(width,height)
        self.actors = {} #dict of GUID:Actor, 0 reserved for open space, 1 reserved for wall
        self.move_to_1 = False
        self.guid_tracker = 100
    def world_step(self):
        from_grid = self.get_active_grid()
        onto_grid = self.get_inactive_grid()
        onto_grid.grid.fill(0)
        for x in range(0,self.width):
            for y in range(0,self.height):
                for z in range(0,SPACES_PER_POSITION):
                    pos = from_grid.grid[x,y,z]

                    if pos[GUID_POS] > 1:
                        actor = self.actors[pos[GUID_POS]]
                        move = actor.get_action(from_grid.mask_visual_field(x,y,actor.traits['visual_radius']),self.actors)
                        if onto_grid.can_make_move(x,y,move):
                            (new_x, new_y) = Grid.new_position(x,y,move)
                            onto_grid.move_actor(new_x,new_y,pos)
        self.move_to_1 = not self.move_to_1
    def get_active_grid(self):
        onto_grid = self.grid_1
        if self.move_to_1:
            onto_grid = self.grid_2
        return onto_grid
    def get_inactive_grid(self):
        onto_grid = self.grid_2
        if self.move_to_1:
            onto_grid = self.grid_1
        return onto_grid
    def add_actor(self, x : int, y : int, actor : Actor):
        guid = self.next_guid()
        self.actors[guid] = actor
        onto_grid = self.get_active_grid()
        onto_grid.grid[x,y] = guid
    def convert_to_image(self):
        img = np.ndarray((self.width,self.height,3),np.uint8)
        img.fill(255)
        out_grid = self.get_active_grid()
        for x in range(0,self.width):
            for y in range(0,self.height):
                pos = out_grid.grid[x,y,0]
                if pos[GUID_POS] > 1:
                    #actor = self.actors[guid]
                    img[x, y] = (pos[CLASS_ID_POS] % 256,(pos[CLASS_ID_POS] + 85) % 256,(pos[CLASS_ID_POS] + 170) % 256) #np.random.randint(255,size=(3))

        return img
    def next_guid(self):
        self.guid_tracker += 1
        return self.guid_tracker

class Renderer(threading.Thread):
    def __init__(self,world : World, frames_per_sec : int):
        super(Renderer,self).__init__()
        self.world = world
        self.frame_time = int((1. / float(frames_per_sec)) * 1000)
    def run(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 700, 700)
        while True:
            cv2.imshow('image', self.world.convert_to_image())
            cv2.waitKey(self.frame_time)

if __name__ == '__main__':
    tick_time = 1. / 60.
    frames_per_sec = 30
    test_world = World(100,100)
    render = Renderer(test_world, frames_per_sec)
    render.start()


    for x in range(25):
        test_world.add_actor(np.random.randint(test_world.width),np.random.randint(test_world.height),RandomMover(0,1))

    while True:
        start = time.time()
        test_world.world_step()
        duration = time.time() - start
        time.sleep(max(0., tick_time - duration))

        #print(time.time() - start)



    cv2.waitKey(0)
    cv2.destroyAllWindows()
