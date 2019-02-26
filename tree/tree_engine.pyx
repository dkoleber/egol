import numpy as np
cimport numpy as np

import time

CATEGORIES = 3
ENERGY_INDEX = 0
OXYGEN_INDEX = 1
NUTRIENTS_INDEX = 2

TYPE_DIRT = 0
TYPE_AIR = 1
TYPE_PLANT = 2
TYPE_EMPTY = 3



def get_type_string(type_int):
    if type_int == TYPE_PLANT:
        return 'plant'
    elif type_int == TYPE_AIR:
        return 'air'
    elif type_int == TYPE_DIRT:
        return 'dirt'
    else:
        return  'empty'

'''

air and dirt give oxygen and nutrients to all plants nearby

spaces that are not plant that accumulate energy >= self.config['grow_threshold'] become plants. Their nutrients and oxygen levels are set to 0

plants with energy > self.config['grow_threshold'] + 8*2 can give 2 energy to all surrounding spaces. 
plants with no energy die and turn into empty
plants with both self.config['oxygen_for_energy'] oxygen and self.config['nutrients_for_energy'] nutrients can remove both to produce self.config['energy_from_photo'] energy
plants lose self.config['energy_decay'] per turn

'''

class Grid:
    def __init__(self, config = None):
        self.config = config
        if config == None:
            self.config = self.default_config()


        self.grid = np.zeros((self.config['width'],self.config['height'],CATEGORIES),dtype=np.int32)
        self.types = np.ndarray((self.config['width'],self.config['height']),dtype=np.int8)
        self.types.fill(TYPE_EMPTY)
        for x in range(self.config['width']):
            for y in range(int(self.config['height']/2)):
                self.types[x,y] = TYPE_AIR
        for x in range(self.config['width']):
            for y in range(int(self.config['height']/2),self.config['height']):
                self.types[x,y] = TYPE_DIRT
        for x in range(int(self.config['width']/5),int(self.config['width']*(4/5))):
            for y in range(int(self.config['height'] / 2)-1, int(self.config['height'] / 2)+1):
                self.types[x,y] = TYPE_PLANT
                self.grid[x, y, ENERGY_INDEX] = 50

    def default_config(self):
        return {
            'width': 50,
            'height': 50,
            'energy_decay': 1,
            'grow_threshold': 10,
            'nutrients_for_energy': 2,
            'oxygen_for_energy': 2,
            'energy_from_photo': 50
        }
        

    def step(self):
        #start_time = time.time()
        values = np.zeros(self.grid.shape, dtype=np.int32)
        has_plant = False
        for x in range(self.config['width']):
            for y in range(self.config['height']):

                type = self.types[x,y]
                nutrients = self.grid[x,y,NUTRIENTS_INDEX]
                oxygen = self.grid[x,y,OXYGEN_INDEX]
                energy = self.grid[x,y,ENERGY_INDEX]
                if type == TYPE_DIRT:
                    self.add_to_adjacents_if_plant(values, x,y, NUTRIENTS_INDEX,1)
                elif type == TYPE_AIR:
                    #print('air: ' + str(x) + '|' + str(y) + '|' + str(time.time()))
                    self.add_to_adjacents_if_plant(values, x, y, OXYGEN_INDEX, 1)
                elif type == TYPE_PLANT: #PLANT
                    has_plant = True
                    values[x, y, ENERGY_INDEX] -= self.config['energy_decay']
                    if nutrients > self.config['nutrients_for_energy'] and oxygen > self.config['oxygen_for_energy']:
                        values[x,y,NUTRIENTS_INDEX] -= self.config['nutrients_for_energy']
                        values[x,y,OXYGEN_INDEX] -= self.config['oxygen_for_energy']
                        values[x,y,ENERGY_INDEX] += self.config['energy_from_photo']
                    else:
                        if nutrients > 1:
                            self.add_to_adjacent_plants_if_less_random(values, x, y, NUTRIENTS_INDEX, nutrients)
                            values[x, y, NUTRIENTS_INDEX] -= nutrients
                        if oxygen > 1:
                            self.add_to_adjacent_plants_if_less_random(values, x, y, OXYGEN_INDEX, oxygen)
                            values[x, y, OXYGEN_INDEX] -= oxygen

                    if energy > self.config['grow_threshold'] + (8*2):
                        grown = self.add_to_adjacents(values, x, y, ENERGY_INDEX, 1)
                        values[x, y, ENERGY_INDEX] -= grown
                    elif energy > self.config['grow_threshold'] + (8):
                        grown = self.add_to_adjacents_if_plant(values, x, y, ENERGY_INDEX, 2)
                        values[x,y,ENERGY_INDEX] -= grown * 2
        #print('1: ' + str(time.time() - start_time))
        #start_time = time.time()
        self.grid = self.grid + values
        for x in range(self.config['width']):
            for y in range(self.config['height']):
                if self.types[x,y] == TYPE_PLANT and self.grid[x,y,ENERGY_INDEX] <= 0:
                    self.types[x,y] = TYPE_EMPTY #np.random.choice([TYPE_DIRT,TYPE_AIR],1)[0]
                    self.grid[x,y] = (0,0,0)
                elif self.grid[x,y,ENERGY_INDEX] > self.config['grow_threshold'] and self.types[x,y] != TYPE_PLANT:
                    self.types[x,y] = TYPE_PLANT
                    self.grid[x,y,NUTRIENTS_INDEX] = 0
                    self.grid[x,y,OXYGEN_INDEX] = 0
        return has_plant
        #print('2: ' + str(time.time() - start_time))

    def convert_to_image(self, nutrient_scale, oxygen_scale, energy_scale):
        #start_time = time.time()
        img = np.zeros((self.config['height'],self.config['width'],3),np.uint8)
        for x in range(self.config['width']):
            for y in range(self.config['height']):
                type = self.types[x,y]
                nutrients = self.grid[x, y, NUTRIENTS_INDEX]
                oxygen = self.grid[x, y, OXYGEN_INDEX]
                energy = self.grid[x, y, ENERGY_INDEX]
                if type == TYPE_DIRT:
                    img[y,x] = (255-81, 255-42, 255-3)
                elif type == TYPE_AIR:
                    img[y,x] = (255-97, 255-149, 255-204)
                elif type == TYPE_PLANT:
                    # nutrients / oxygen gets up to around 15
                    # energy gets up to around 40
                    total_scale = float(nutrient_scale + oxygen_scale + energy_scale) / 100.
                    adjusted_nutrients = (float(nutrient_scale) / 100.) * (float(nutrients) / 15.)
                    adjusted_oxygen = (float(oxygen_scale) / 100.) * (float(oxygen) / 15.)
                    adjusted_energy = (float(energy_scale) / 100.) * (float(energy) / 40.)
                    total_value = min(((adjusted_nutrients + adjusted_oxygen + adjusted_energy) / max(total_scale,1.)), 1.)
                    r = int(255. * total_value)
                    g = 130 + int((255.-130.)* total_value)
                    b = 25 + int((255.-25.) * total_value)
                    img[y,x] = (r, g, b)
                else:
                    img[y,x] = (0,0,0)
        #print(time.time() - start_time)
        return img

    def add_to_adjacents(self, grid, x, y, index, amount_per):
        count = 0
        for x1 in range(max(0, x - 1), min(self.config['width'], x + 2)):
            for y1 in range(max(0, y - 1), min(self.config['height'], y + 2)):
                grid[x1,y1,index] += amount_per
                count += 1
        return count

    def add_to_adjacents_if_plant(self, grid, x, y, index, amount_per):
        count = 0
        for x1 in range(max(0, x - 1), min(self.config['width'], x + 2)):
            for y1 in range(max(0, y - 1), min(self.config['height'], y + 2)):
                if self.types[x1,y1] == TYPE_PLANT:
                    grid[x1,y1,index] += amount_per
                    count += 1
        return count

    def add_to_adjacent_plants_if_less_random(self, grid, x, y, index, amount_total):
        list_of_lower = []
        for x1 in range(max(0, x - 1), min(self.config['width'], x + 2)):
            for y1 in range(max(0, y - 1), min(self.config['height'], y + 2)):
                if self.types[x1, y1] == TYPE_PLANT and self.grid[x,y,index] > self.grid[x1,y1,index]:
                    list_of_lower.append([x1,y1])
        amount_per = 0
        if amount_total < len(list_of_lower):
            amount_per = 1
            list_of_lower = list_of_lower[:amount_total]
        elif len(list_of_lower) > 0:
            amount_per = int(amount_total / len(list_of_lower))

        np.random.shuffle(list_of_lower)
        amount_remaining = amount_total
        for coord in list_of_lower:
            amount_distributed = min(amount_remaining,amount_per)
            grid[coord[0],coord[1],index] += amount_distributed
            amount_remaining -= amount_distributed

    def get_stats(self):
        AVERAGE_INDEX = 0
        MAX_INDEX = 1
        TOTAL_INDEX = 2
        stats = {'energy':[0.,0.,0.], #arranged as average, max, total
                 'nutrients':[0.,0.,0.],
                 'oxygen':[0.,0.,0.],
                 'total_plants':0
        }
        for x in range(self.config['width']):
            for y in range(self.config['height']):
                if self.types[x,y] == TYPE_PLANT:
                    stats['total_plants'] += 1
                    nutrients = self.grid[x, y, NUTRIENTS_INDEX]
                    oxygen = self.grid[x, y, OXYGEN_INDEX]
                    energy = self.grid[x, y, ENERGY_INDEX]
                    stats['energy'][AVERAGE_INDEX] += energy
                    stats['energy'][TOTAL_INDEX] += energy
                    if stats['energy'][MAX_INDEX] < energy:
                        stats['energy'][MAX_INDEX] = energy

                    stats['nutrients'][AVERAGE_INDEX] += nutrients
                    stats['nutrients'][TOTAL_INDEX] += nutrients
                    if stats['nutrients'][MAX_INDEX] < nutrients:
                        stats['nutrients'][MAX_INDEX] = nutrients

                    stats['oxygen'][AVERAGE_INDEX] += oxygen
                    stats['oxygen'][TOTAL_INDEX] += oxygen
                    if stats['oxygen'][MAX_INDEX] < oxygen:
                        stats['oxygen'][MAX_INDEX] = oxygen

        stats['energy'][AVERAGE_INDEX] = float(stats['energy'][AVERAGE_INDEX]) / max(float(stats['total_plants']), 1.)
        stats['nutrients'][AVERAGE_INDEX] = float(stats['nutrients'][AVERAGE_INDEX]) / max(float(stats['total_plants']), 1.)
        stats['oxygen'][AVERAGE_INDEX] = float(stats['oxygen'][AVERAGE_INDEX]) / max(float(stats['total_plants']), 1.)

        return stats

    def get_config(self):
        return self.config

