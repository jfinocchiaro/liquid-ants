import numpy as np
from random import *


DEFAULT_RADIUS = 3
num_ants = 100
action_set = range(num_ants) + ['N', 'S', 'E', 'W']
M = 100


#id_num is the ant's identification number, used for indexing each ant
#action_set is the set of actions the ant can take in the next time step
#position is the (x,y) coordinate where the ant is currently located
#radius is their radius of vision

class Ant():
    def __init__(self):
        self.id_num = 0
        self.confidence = randint(0,4)
        self.radius = DEFAULT_RADIUS
        self.action_set = action_set
        self.position = (randint(0, M-1), randint(0, M-1))

    def __init__(self, id_num, action_set, radius, confidence, position):
        self.id_num = id_num
        self.radius = radius
        self.action_set = action_set
        self.position = position


#tl_position is the location of the top-left corner of the transported object
#br_position is the location of the bottom-right corner of the transported object
#weight is the number of ants needed to actually move the object
class Transport():
    def __init__(self, tl_position, br_position, weight):
        self.tl_position = tl_position
        self.br_position = br_position
        self.weight = weight
'''
    def __init__(self):
        self.tl_position = (0,0)
        self.br_position = (4,4) #come back to this?
        self.weight = 12
'''
