import json
import threading
from pyximport import pyximport
import time
import cv2
import numpy as np
import os.path
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, qApp, QLabel, QLineEdit, QFileDialog, QPushButton

pyximport.install(language_level=3,setup_args={"include_dirs":np.get_include()})
import ant_engine as engine
from ant_engine import World



'''
TODO
-select world type
-load/save
-create your own colors/directions mode
- pause button

'''


IMAGE_FILE_TYPE = '.bmp'
DATA_FILE_TYPE = '.json'

### Util methods
def try_func(default = None):
    def ignore(function):
        def _ignore(*args, **kwargs):
            try:
                return function(*args,**kwargs)
            except:
                return default
        return _ignore
    return ignore
def int_parse(val, default):
    parse =  try_func(default)(int)
    return parse(val)
def ends_with(string, ending):
    return len(string) >= len(ending) and string[-len(ending):] == ending


class Renderer(threading.Thread):
    def __init__(self,world : World, frames_per_sec : int):
        super(Renderer,self).__init__()
        self.world = world
        self.frame_time = int((1. / float(frames_per_sec)) * 1000)
        self.is_paused = False

    def run(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 500, 500)

        def on_fps_change(x):
            self.frame_time = int((1. / float(max(x,1))) * 1000)

        cv2.createTrackbar('fps', 'image', 1, 60, on_fps_change)

        while True:
            if self.is_paused:
                continue
            start_time = time.time()
            cv2.imshow('image', self.world.convert_to_image())
            cv2.waitKey(self.frame_time)

class ControlsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.world_mode = 2
        self.frames_per_second = 30
        self.steps_per_second = 500


        self.initialize_components()

    def initialize_components(self):

        new_world_action = QAction('New Simulation', self)
        new_world_action.setShortcut('Ctrl+N')
        new_world_action.setStatusTip('New Simulation')
        new_world_action.triggered.connect(self.new_world_handler)

        load_world_action = QAction('Load World', self)
        load_world_action.setShortcut('Ctrl+D')
        load_world_action.setStatusTip('Load World')
        load_world_action.triggered.connect(self.load_world_handler)

        save_world_action = QAction('Save World', self)
        save_world_action.setShortcut('Ctrl+S')
        save_world_action.setStatusTip('Save World')
        save_world_action.triggered.connect(self.save_world_handler)

        steps_per_second_edit = QLineEdit(str(self.steps_per_second), self)
        steps_per_second_edit.textChanged.connect(self.sps_changed_handler)
        steps_per_second_edit.move(10,50)

        pause_button = QPushButton('Pause', self)
        pause_button.move(10,100)
        pause_button.clicked.connect(self.pause_handler)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(new_world_action)
        file_menu.addAction(load_world_action)
        file_menu.addAction(save_world_action)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Controls')
        self.show()

        self.new_world_handler()

    def new_world_handler(self, world = None):
        paused_before = False

        if hasattr(self, 'renderer'): #stop rendering since there's about to not be a world to render
            self.renderer.is_paused = True

        if world == None: #make a new world
            self.world = World(50, 50, self.world_mode)
        else:
            self.world = world

        if hasattr(self, 'runner'): #stop the world runner if it exists
            paused_before = self.runner.is_paused
            self.runner.is_running = False

        self.runner = WorldRunner(self.world, self.steps_per_second) #create a new runner
        self.runner.is_paused = paused_before

        if hasattr(self, 'renderer'): #create a new renderer or set it to render a new world
            self.renderer.world = self.world
        else:
            self.renderer = Renderer(self.world,self.frames_per_second)
            self.renderer.start()

        self.renderer.is_paused = False #unpause rendering
        self.runner.start() #start the new runner

    def load_world_handler(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        full_path, _ = QFileDialog.getOpenFileName(self, 'Select File to Load', '', 'Saved Simulation Files (*' + IMAGE_FILE_TYPE + ')', options=options)
        if full_path:
            directory, name = os.path.split(full_path)
            if ends_with(name, IMAGE_FILE_TYPE):
                data_name = name.replace(IMAGE_FILE_TYPE, DATA_FILE_TYPE)
                data_path = os.path.join(directory, data_name)
                if os.path.exists(data_path):
                    world = World(50,50,0)
                    with open(data_path) as fl:
                        data = json.load(fl)
                    world.set_config(data)
                    img = cv2.imread(full_path,cv2.IMREAD_COLOR)
                    world.set_grid(img)
                    self.new_world_handler(world)

    def save_world_handler(self):
        if hasattr(self, 'world'):
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            full_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Saved Simulation Files (*' + IMAGE_FILE_TYPE + ')', options=options)
            if full_path:
                directory, name = os.path.split(full_path)
                if not ends_with(name, IMAGE_FILE_TYPE):
                    name += IMAGE_FILE_TYPE
                data_name = name.replace(IMAGE_FILE_TYPE,DATA_FILE_TYPE)
                data_path = '/'.join([directory, data_name])
                paused_before = self.runner.is_paused
                self.runner.is_paused = True
                data = self.world.get_config()
                with open(data_path, 'w+') as fl:
                    json.dump(data, fl, indent=4)
                cv2.imwrite('/'.join([directory, name]), self.world.get_grid())
                self.runner.is_paused = paused_before

    def sps_changed_handler(self,text):
        if hasattr(self, 'runner'):
            self.steps_per_second = int_parse(text, self.runner.max_steps_per_second)
            self.runner.max_steps_per_second = self.steps_per_second

    def pause_handler(self):
        self.runner.is_paused = not self.runner.is_paused

class ControlsApp(threading.Thread):
    def __init__(self):
        super(ControlsApp, self).__init__()

    def run(self):
        app = QApplication([])
        window = ControlsWindow()
        app.exec_()

class WorldRunner(threading.Thread):
    def __init__(self,grid, max_sps = 5):
        super(WorldRunner,self).__init__()
        self.grid = grid
        self.steps_per_second = 1     #actual time for 1 world step  (written by this, read by others)
        self.max_steps_per_second = max_sps #minimum time for 1 world step (written by others, read by this)
        self.steps = 0
        self.is_running =  True
        self.is_paused = False
    def run(self):
        while self.is_running:
            if self.is_paused:
                continue
            start = time.time()
            self.grid.step()
            self.steps += 1
            duration = time.time() - start
            self.steps_per_second = 1. / max(duration,0.001)
            stop_time = 1. / float(max(self.max_steps_per_second, 1))
            time.sleep(max(0, stop_time - duration))


if __name__ == '__main__':
    # frames_per_sec = 30
    # test_world = World(50,50)
    # render = Renderer(test_world, frames_per_sec)
    # render.start()
    controls = ControlsApp()
    controls.start()


    stop_time = .001






    # cv2.waitKey(0)
    # cv2.destroyAllWindows()