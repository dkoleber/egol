import sqlite3 as sql
import matplotlib.pyplot as plt
import numpy as np
import os

DATABASE_NAME = 'tree_stats.db'
SIMS_TABLE_NAME = 'sims_table'
STATS_TABLE_NAME = 'stats_table'

class TreeStats:
    '''
    sim_name is None when you're looking to do analytics on multiple sims
    config is None but sim_name is not None when you're looking to do analytics on a single sim
    config is not None and sim_name is not None when you're looking to enter data into the database for that sim_name
    '''
    def __init__(self, sim_name = None, config = None):
        self.connect_to_database()
        c = self.c
        self.pk = sim_name

        if sim_name == None:
            c.execute("SELECT name FROM %s WHERE name='%s'" % (SIMS_TABLE_NAME, self.pk))
            if len(c.fetchall()) == 0 and config != None:
                c.execute("INSERT INTO %s VALUES ('%s', %d, %d, %d, %d, %d, %d, %d)" % (
                          SIMS_TABLE_NAME,
                          self.pk,
                          config['width'],
                          config['height'],
                          config['energy_decay'],
                          config['grow_threshold'],
                          config['nutrients_for_energy'],
                          config['oxygen_for_energy'],
                          config['energy_from_photo']))
                self.conn.commit()

    def add_entry(self, steps, stats):
        if self.pk == None:
            return
        self.c.execute("INSERT INTO %s VALUES ('%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)" % (
            STATS_TABLE_NAME,
            self.pk,
            steps,
            stats['energy'][0],
            stats['energy'][1],
            stats['energy'][2],
            stats['nutrients'][0],
            stats['nutrients'][1],
            stats['nutrients'][2],
            stats['oxygen'][0],
            stats['oxygen'][1],
            stats['oxygen'][2],
            stats['total_plants']))
        self.conn.commit()
    def connect_to_database(self):
        self.conn = sql.connect(DATABASE_NAME)
        self.c = self.conn.cursor()
        c = self.c

        c.execute("SELECT name FROM sqlite_master where type='table' AND name='%s'" % SIMS_TABLE_NAME)
        if len(c.fetchall()) == 0: #add the table if it doesn't exist
            c.execute("CREATE TABLE %s (name text, \
                        width real, height real, energy_decay real, \
                        grow_threshold real, nutrients_for_energy real, \
                        oxygen_for_energy real, energy_from_photo real)" % SIMS_TABLE_NAME)
            self.conn.commit()

        c.execute("SELECT name FROM sqlite_master where type='table' AND name='%s'" % STATS_TABLE_NAME)
        if len(c.fetchall()) == 0: #add the table if it doesn't exist
            c.execute("CREATE TABLE %s (name text, steps real, \
                        energy_average real, energy_max real, energy_total real, \
                        nutrients_average real, nutrients_max real, nutrients_total real, \
                        oxygen_average real, oxygen_max real, oxygen_total real, \
                        total_plants real)" % STATS_TABLE_NAME)
            self.conn.commit()
    def show_stats(self):
        if self.pk == None:
            return
        self.c.execute("SELECT * FROM %s WHERE name='%s'" % (STATS_TABLE_NAME, self.pk))
        values = np.array([ list(x[1:]) for x in list(self.c.fetchall())])

        rows = 3
        cols = 3
        pos = 1


        scr = plt.figure()
        energy = scr.add_subplot(rows, cols, pos)
        energy.set_title('Energy')
        energy.plot(values[:,0],values[:,1], label='average energy')
        energy.plot(values[:,0],values[:,2], label='max energy')
        energy.legend(loc='upper right')
        pos += 1

        energy_total = scr.add_subplot(rows, cols, pos)
        energy_total.set_title('Total Energy')
        energy_total.plot(values[:, 0], values[:, 3], label='total energy')
        pos += 1

        plants_total = scr.add_subplot(rows, cols, pos)
        plants_total.set_title('Total Plants')
        plants_total.plot(values[:, 0], values[:, 10], label='total plants')
        pos += 1

        nutrients = scr.add_subplot(rows, cols, pos)
        nutrients.set_title('Nutrients')
        nutrients.plot(values[:,0],values[:,4], label='average nutrients')
        nutrients.plot(values[:,0],values[:,5], label='max nutrients')
        nutrients.legend(loc='upper right')
        pos += 1

        nutrients_total = scr.add_subplot(rows, cols, pos)
        nutrients_total.set_title('Total Nutrients')
        nutrients_total.plot(values[:, 0], values[:, 6], label='total nutrients')
        pos += 2

        oxygen = scr.add_subplot(rows, cols, pos)
        oxygen.set_title('Oxygen')
        oxygen.plot(values[:, 0], values[:,7], label='average oxygen')
        oxygen.plot(values[:, 0], values[:,8], label='max oxygen')
        oxygen.legend(loc='upper right')
        pos += 1

        oxygen_total = scr.add_subplot(rows, cols, pos)
        oxygen_total.set_title('Total Oxygen')
        oxygen_total.plot(values[:, 0], values[:, 9], label='total oxygen')
        pos += 2

        plt.show()
        #print(values)
    def load_config(self,sim_name):
        self.c.execute("SELECT * FROM %s WHERE name='%s'" % (SIMS_TABLE_NAME,sim_name))
        vals = self.c.fetchall()[0]
        return {
            'width':vals[1],
            'height':vals[2],
            'energy_decay':vals[3],
            'grow_threshold':vals[4],
            'nutrients_for_energy':vals[5],
            'oxygen_for_energy':vals[6],
            'energy_from_photo':vals[7]
        }
    def load_stats(self,sim_name):
        self.c.execute("SELECT * FROM %s WHERE name='%s' ORDER BY steps ASC" % (STATS_TABLE_NAME,sim_name))
        vals = self.c.fetchall()
        res = []
        for x in vals:
            res.append({
                'steps':x[1],
                'energy_average':x[2],
                'energy_max':x[3],
                'energy_total':x[4],
                'nutrients_average':x[5],
                'nutrients_max':x[6],
                'nutrients_total':x[7],
                'oxygen_average':x[8],
                'oxygen_max':x[9],
                'oxygen_total':x[10],
                'total_plants':x[11]
            })
        return res
    def multi_stat(self):
        self.c.execute("SELECT name FROM %s" % (SIMS_TABLE_NAME))
        all_sims = list(self.c.fetchall())
        items = {name:{'config': self.load_config(name),'stats':self.load_stats(name)} for name in all_sims}





if __name__ == '__main__':
    #'tree_1551211346.1682978'
    #'tree_1551211388.966037'
    #'tree_1551211441.7141519'
    #'tree_1551211467.8221138'
    stats_manager = TreeStats('tree_1551211388.966037')
    stats_manager.show_stats()