import numpy as np
from random import *


DEFAULT_RADIUS = 3
num_ants = 100
full_action_set = ['N', 'S', 'E', 'W', 'G'] + range(1,num_ants+1)
M = 100


#id_num is the ant's identification number, used for indexing each ant
#action_set is the set of actions the ant can take in the next time step
#position is the (x,y) coordinate where the ant is currently located
#radius is their radius of vision

class Ant():
    # def __init__(self):
    #     self.id_num = 0
    #     self.confidence = randint(0,4)
    #     self.radius = DEFAULT_RADIUS
    #     self.action_set = full_action_set
    #     self.position = (randint(0, M-1), randint(0, M-1))
    #     self.vote = 'N'
    #     self.carrying = False

    def __init__(self, id_num, action_set, radius, confidence, position, vote, carrying, see_object, previous_move = 'N'):
        self.id_num = id_num
        self.action_set = action_set
        self.radius = radius
        self.confidence = confidence
        self.position = position
        self.vote = vote
        self.carrying = carrying
        self.see_object = see_object
        self.previous_move = previous_move


#tl_position is the location of the top-left corner of the transported object
#br_position is the location of the bottom-right corner of the transported object
#weight is the number of ants needed to actually move the object
class Transport():
    def __init__(self, tl_position, br_position, weight, carried_by):
        self.tl_position = tl_position
        self.br_position = br_position
        self.weight = weight
        self.carried_by = carried_by
