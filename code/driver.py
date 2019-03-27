import numpy as np
from random import *
import ants_and_objects
from math import *

#TODO: fix hack of marking environment with addition of number
#TODO: make home base more than one tile
def initializeEnv(m, num_ants, random_pos, radius, obj_size, obj_mark_num):
    env = np.zeros((m,m))
    ant_dict = {}

    #ant placement
    #place ants randomly in the environment
    if random_pos:
        pass
    #place ants in a blob that is (sqrt n x sqrt n)
    else:
        row_length = np.ceil(sqrt(num_ants))
        corner = (randint(0, m - row_length), randint(0, m - row_length))
        for id_num in range(1, num_ants+1):
            pos = (int(corner[0] + ((id_num-1) % row_length)), corner[1] + int((id_num-1) / row_length))
            ant_dict[id_num] = ants_and_objects.Ant(id_num, [], radius, 0, pos)
            env[pos] = id_num

        print env

        #place the object on top of the blob for now
        trans_obj = ants_and_objects.Transport(corner, corner + (obj_size, obj_size), int(num_ants / 10)) #weight can change later
        for i in range(corner[0], corner[0]+ obj_size):
            for j in range(corner[1], corner[1]+ obj_size):
                env[(i,j)] += obj_mark_num

        print env

        #initialize home base
        in_obj = 1
        while (in_obj):
            hb_pos = (randint(0, m-1), randint(0, m-1))
            if (trans_obj.tl_position[0] <= hb_pos[0] <= trans_obj.br_position[0]) and (trans_obj.tl_position[1] <= hb_pos[1] <= trans_obj.br_position[1]):
                pass
            else:
                in_obj = 0

        env[hb_pos] = -100 #marking in environment where home base is

    return env, ant_dict

def main(m, num_ants, random_pos, radius, obj_size, obj_mark_num):
    [env, ant_dict] = initializeEnv(m, num_ants, random_pos, radius, obj_size, obj_mark_num)

    print env
    print ant_dict[1].position

if __name__ == "__main__":
    m = 10
    num_ants = 10
    random_pos = 0
    radius = 5
    obj_size = 1
    obj_mark_num = 50

    main(m, num_ants, random_pos, radius, obj_size, obj_mark_num)
