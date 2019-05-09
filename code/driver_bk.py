import numpy as np
from numpy.random import *
import ants_and_objects as a_o
from math import *
from matplotlib import pyplot as plt
from time import sleep
np.set_printoptions(suppress=True)

#TODO: fix hack of marking environment with addition of number
#TODO: make home base more than one tile
#TODO: Limit carrier ant's vision
#TODO: Currently gives vote to first agent with highest confidence. Need to add some tie breaking scheme.
#TODO: Merge see_hb and move_towards_hb functions
#TODO: Visualization
#TODO: Debug

#NOTE: Added action 'G' which means reached home and so "Go into the nest"
#NOTE: Made updating confidences second thing and merged it with broadcasting confidence
#NOTE: It's a square lattive now for simplicity of the 'physics'

def vis_env_mapping(environment, mark_number):
    mapped_env = np.zeros((environment.shape))
    for i in range(environment.shape[0]):
        for j in range(environment.shape[1]):
            if environment[i,j] >= mark_number:
                mapped_env[i,j] = 1
            elif environment[i,j] > 0:
                mapped_env[i,j] = 2
            elif environment[i,j] < 0:
                mapped_env[i,j] = 3
    return mapped_env

def ascii_vis(environment, mark_number):
    mapped_env = vis_env_mapping(environment, mark_number)
    print('_'*environment.shape[1])
    to_print = ''
    for i in range(environment.shape[0]):
        to_print += '| '
        for j in range(environment.shape[1]):
            if mapped_env[i,j] == 1:
                to_print += 'O'
            elif mapped_env[i,j] == 2:
                to_print += 'A'
            elif mapped_env[i,j] == 3:
                to_print += 'H'
            else:
                to_print += ' '
        to_print += ' |'
        print(to_print)
        to_print = ''
    print('_'*environment.shape[1])

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
        corner = [randint(0, m - row_length), randint(0, m - row_length - (num_ants%row_length))]
        for id_num in range(1, num_ants+1):
            pos = [int(corner[0] + ((id_num-1) % row_length)), corner[1] + int((id_num-1) / row_length)]
            ant_dict[id_num] = a_o.Ant(id_num, [], radius, 0, pos, choice(['N', 'S', 'E', 'W']), False, False)
            env[pos[0],pos[1]] = id_num

        #place the object on top of the blob for now
        if obj_size == 1: 
            trans_obj = a_o.Transport([corner[0],corner[1]], [corner[0],corner[1]], int(num_ants / 10), []) #weight can change later
        else:
            trans_obj = a_o.Transport([corner[0],corner[1]], [corner[0]+obj_size-1, corner[1]+obj_size-1], int(num_ants / 10), []) #weight can change later
        for i in range(corner[0], corner[0]+ obj_size):
            for j in range(corner[1], corner[1]+ obj_size):
                ant_dict[env[(i,j)]].carrying = True
                ant_dict[env[(i,j)]].see_object = True
                # ant_dict[env[(i,j)]].radius = 1 #if the ant is carrying the object, we want it to have vision radius 1.
                trans_obj.carried_by += [env[i,j]] 
                env[(i,j)] += obj_mark_num

        #initialize home base. while loop makes sure that we don't start on home base because that's no fun
        in_obj = 1
        while (in_obj):
            hb_pos = [randint(0, m-1), randint(0, m-1)]
            if (trans_obj.tl_position[0] <= hb_pos[0] <= trans_obj.br_position[0]) and (trans_obj.tl_position[1] <= hb_pos[1] <= trans_obj.br_position[1]):
                pass
            else:
                in_obj = 0

        env[hb_pos[0],hb_pos[1]] = -100 #marking in environment where home base is.  by initialization, should have been 0 before.

    return env, ant_dict, trans_obj

def see_hb(environment, position, radius):
    for i in range(max(position[0]-radius,0),min(position[0]+radius,m-1)):
        for j in range(max(position[1]-radius,0),min(position[1]+radius,m-1)):
            if environment[i,j] == -100:
                return True

#if you see home base move towards it.
#preference toward vertical movement, but once we're in the correct row, move horizontally toward home base
def move_towards_hb(environment, position, radius):
    for i in range(max(position[0]-radius,0),min(position[0]+radius,m-1)):
        for j in range(max(position[1]-radius,0),min(position[1]+radius,m-1)):
            if environment[i,j] == -100:
                if i < position[0]:
                    return 'N'
                elif i > position[0]:
                    return 'S'
                elif j < position[1]:
                    return 'W'
                elif j >  position[1]:
                    return 'E'
                else:
                    return 'G'

def tug_o_war(votes, obj, m):
    #preprocessing to change the votes if the object can't move in a given direction
    obj_height = obj.br_position[0]-obj.tl_position[0]
    obj_width = obj.br_position[1]-obj.tl_position[1]
    if obj.tl_position[0] == 0:
        votes[0] = -1
    if obj.tl_position[1] == 0:
        votes[3] = -1
    if obj.br_position[0] == m-1:
        votes[1] = -1
    if obj.br_position[1] == m-1:
        votes[2] = -1

    # #note, this implicitly has tiebreaker N > S > E > W
    # winner = votes.index(max(votes))

    potential_winners = [idx for idx in range(4) if votes[idx] == max(votes)]
    winner = choice(potential_winners)

    if winner == 0:
        return 'N'
    elif winner == 1:
        return 'S'
    elif winner == 2:
        return 'E'
    else:
        return 'W'

def actuate_movement(environment, ant, obj, queue, id_num):
    if ant.vote == 'N':
        if ant.position[0]-1 < 0:
            pass
        elif id_num in obj.carried_by:
            pass
        elif environment[ant.position[0]-1,ant.position[1]] > 0:
            queue += [id_num]
        else:
            if environment[ant.position[0]-1, ant.position[1]] != -100:
                environment[ant.position[0]-1, ant.position[1]] = environment[ant.position[0],ant.position[1]]
            environment[ant.position[0],ant.position[1]] = 0
            ant.position[0] -= 1  

    elif ant.vote == 'S':
        if ant.position[0]+1 >= m:
            pass
        elif id_num in obj.carried_by:
            pass
        elif environment[ant.position[0]+1,ant.position[1]] > 0:
            queue += [id_num]
        else:
            if environment[ant.position[0]+1, ant.position[1]] != -100:
                environment[ant.position[0]+1, ant.position[1]] = environment[ant.position[0],ant.position[1]]
            environment[ant.position[0],ant.position[1]] = 0
            ant.position[0] += 1

    elif ant.vote == 'E':
        if ant.position[1]+1 >= m:
            pass
        elif id_num in obj.carried_by:
            pass
        elif environment[ant.position[0],ant.position[1]+1] > 0:
            queue += [id_num]
        else:
            if environment[ant.position[0], ant.position[1]+1] != -100:
                environment[ant.position[0], ant.position[1]+1] = environment[ant.position[0],ant.position[1]]
            environment[ant.position[0],ant.position[1]] = 0
            ant.position[1] += 1

    elif ant.vote == 'W':
        if ant.position[1]-1 < 0:
            pass
        elif id_num in obj.carried_by:
            pass
        elif environment[ant.position[0],ant.position[1]-1] > 0:
            queue += [id_num]
        else:
            if environment[ant.position[0], ant.position[1]-1] != -100:
                environment[ant.position[0], ant.position[1]-1] = environment[ant.position[0],ant.position[1]]
            environment[ant.position[0],ant.position[1]] = 0
            ant.position[1] -= 1
    
    return environment, queue

def actuate_object_movement(environment, obj, ant_dict, obj_marker):
    path_clear = True
    for id_num in obj.carried_by: 
        ant = ant_dict[id_num]
        if ant.vote == 'N':
            if ant.position[0]-1 < 0:
                path_clear = False
            elif environment[ant.position[0]-1,ant.position[1]] > 0:
                if (environment[ant.position[0]-1,ant.position[1]]-obj_marker) not in obj.carried_by:
                    path_clear = False

        elif ant.vote == 'S':
            if ant.position[0]+1 >= m:
                path_clear = False
            elif environment[ant.position[0]+1,ant.position[1]] > 0:
                if (environment[ant.position[0]+1,ant.position[1]]-obj_marker) not in obj.carried_by:
                    path_clear = False

        elif ant.vote == 'E':
            if ant.position[1]+1 >= m:
                path_clear = False
            elif environment[ant.position[0],ant.position[1]+1] > 0:
                if (environment[ant.position[0],ant.position[1]+1]-obj_marker) not in obj.carried_by:
                    path_clear = False

        elif ant.vote == 'W':
            if ant.position[1]-1 < 0:
                path_clear = False
            elif environment[ant.position[0],ant.position[1]-1] > 0:
                if (environment[ant.position[0],ant.position[1]-1]-obj_marker) not in obj.carried_by:
                    path_clear = False

    if path_clear:
        for id_num in obj.carried_by: 
            ant = ant_dict[id_num]
            if ant.vote == 'N':
                if environment[ant.position[0], ant.position[1]] != -100:
                    environment[ant.position[0],ant.position[1]] = 0
                ant.position[0] -= 1

            elif ant.vote == 'S':
                if environment[ant.position[0], ant.position[1]] != -100:
                    environment[ant.position[0],ant.position[1]] = 0
                ant.position[0] += 1

            elif ant.vote == 'E':
                if environment[ant.position[0], ant.position[1]] != -100:
                    environment[ant.position[0],ant.position[1]] = 0
                ant.position[1] += 1

            elif ant.vote == 'W':
                if environment[ant.position[0], ant.position[1]] != -100:
                    environment[ant.position[0],ant.position[1]] = 0
                ant.position[1] -= 1

        for id_num in obj.carried_by:
            ant = ant_dict[id_num]
            if environment[ant.position[0], ant.position[1]] != -100:
                environment[ant.position[0],ant.position[1]] = id_num + obj_marker

        if ant.vote == 'N':
            obj.tl_position[0] -= 1
            obj.br_position[0] -= 1

        elif ant.vote == 'S':
            obj.tl_position[0] += 1
            obj.br_position[0] += 1

        elif ant.vote == 'E':
            obj.tl_position[1] += 1
            obj.br_position[1] += 1

        elif ant.vote == 'W':
            obj.tl_position[1] -= 1
            obj.br_position[1] -= 1

    return environment


def main(m, num_ants, random_pos, radius, obj_size, obj_mark_num, volunteer_prob):
    env, ant_dict, trans_obj = initializeEnv(m, num_ants, random_pos, radius, obj_size, obj_mark_num)

    found_hb = False
    time = 0
    TIME_LIMIT = 10000


    # Enter action sequence until home base is found.
    while(not found_hb) and (time <= TIME_LIMIT):
        #Check if goal was reached
        # for i in range(trans_obj.tl_position[0],trans_obj.br_position[0]+1):
        #     for j in range(trans_obj.tl_position[1],trans_obj.br_position[1]+1):
        #         if env[i,j] == -100:
        #             found_hb = True
        #             print("Simulation Complete after " + str(time) + " time steps.")
        #             print (env)
        #             return 0

        #Temp completion check until object updates are set up
        for id_num in range(1, num_ants+1):
            if ant_dict[id_num].carrying:
                if env[ant_dict[id_num].position[0],ant_dict[id_num].position[1]] == -100:
                    found_hb = True
                    print("Simulation Complete after " + str(time) + " time steps.")
                    # print (env)
                    quit()

        time += 1
        print '~~~~~~~~~~~~~~~~~~~~~~~Time ' + str(time) + '~~~~~~~~~~~~~~~~~~~~~~~~~~'

        #Update action set by seeing who is in my radius
        for id_num in range(1, num_ants+1):
            ant_dict[id_num].action_set = ['N', 'S', 'E', 'W', 'G']

            for i in range(max(ant_dict[id_num].position[0]-radius,0),min(ant_dict[id_num].position[0]+radius,m-1)):
                for j in range(max(ant_dict[id_num].position[1]-radius,0),min(ant_dict[id_num].position[1]+radius,m-1)):
                    if (i != ant_dict[id_num].position[0]) and (j != ant_dict[id_num].position[1]):
                        if env[i,j]>0:
                            if env[i,j]-obj_mark_num < 0:
                                ant_dict[id_num].action_set += [env[i,j]]
                            elif env[i,j]-obj_mark_num > 0:
                                ant_dict[id_num].action_set += [env[i,j]-obj_mark_num]

        #Update/broadcast confidences
        queue = []

        for id_num in range(1, num_ants+1):
            if see_hb(env,ant_dict[id_num].position,ant_dict[id_num].radius) == True:
                ant_dict[id_num].confidence = 4
            #why is this an if else?  so if they can't see the item, they get added to the queue, which has all of the vote delegators?
            #G: We just had to make sure the ones who saw hb were updated so that in the pass through the others they could see if they saw an informed individual or not
            else:
                queue += [id_num]
        for iters in queue:
            for id_num in queue:
                max_confidence = ant_dict[id_num].confidence

                for act in ant_dict[id_num].action_set:
                    if act not in ['N', 'S', 'E', 'W', 'G']:
                        if ant_dict[act].confidence > max_confidence:
                            max_confidence = ant_dict[act].confidence

                if max_confidence in [3,4]:
                    ant_dict[id_num].confidence = 3
                elif not ant_dict[id_num].carrying:
                    ant_dict[id_num].confidence = binomial(1, volunteer_prob) + 1
                else: #ant is carrying the object
                    ant_dict[id_num].confidence = 0

        # Choose an action and broadcast it
        # what's the difference between this and the loop above, other than it being run over every ant this time?
        # G: Above they updated confidences. Now they can choose how to actually act/delegate votes based on confidences that are up to date (otherwise we are doing it on old info)
        # G: What did sorting do for us?
        for id_num in range(1, num_ants+1):
            # Look at neighbors in view to decide who to cast a vote towards
            if ant_dict[id_num].confidence <= 3:
                max_confidence = ant_dict[id_num].confidence
                max_confidence_id = id_num

                for act in ant_dict[id_num].action_set:
                    if act not in ['N', 'S', 'E', 'W', 'G']:
                        if ant_dict[act].confidence > max_confidence:
                            max_confidence = ant_dict[act].confidence
                            max_confidence_id = act
                            ant_dict[id_num].vote = act

                #if you're casting your own vote
                #voting in a random direction since you ain't actually educated
                if max_confidence_id == id_num:
                    ant_dict[id_num].vote = ant_dict[id_num].action_set[randint(0,4)]

            #if you're educated, move towards home base.
            else:
                ant_dict[id_num].vote = move_towards_hb(env,ant_dict[id_num].position,radius)

            # if ant_dict[id_num].carrying:
            #     print('Carrier ant wants to vote: ' + str(ant_dict[id_num].vote))

        # Move in direction your vote went
        queue = [] #Who needs to move
        obj_direction_vote = [0,0,0,0] #Where do those people want to move

        #First update votes on others to votes on a direction
        for id_num in range(1, num_ants+1):
            while(ant_dict[id_num].vote not in ['N', 'S', 'E', 'W', 'G']):
                ant_dict[id_num].vote = ant_dict[ant_dict[id_num].vote].vote

        #Decide which way the object will move
        for id_num in trans_obj.carried_by:
                if ant_dict[id_num].vote == 'N':
                    obj_direction_vote[0] += 1
                elif ant_dict[id_num].vote == 'S':
                    obj_direction_vote[1] += 1
                elif ant_dict[id_num].vote == 'E':
                    obj_direction_vote[2] += 1
                elif ant_dict[id_num].vote == 'W':
                    obj_direction_vote[3] += 1
        obj_dir = tug_o_war(obj_direction_vote, trans_obj, m)
        for id_num in trans_obj.carried_by:
            # print('Carrier ant voted: ' + str(ant_dict[id_num].vote))
            # print("Votes cast were: " + str(obj_direction_vote))
            # print('Object position: ' + str(trans_obj.tl_position) + ", " + str(trans_obj.br_position))
            # print('Carrier position: ' + str(ant_dict[id_num].position))
            # print(ant_dict[id_num].confidence)
            ant_dict[id_num].vote = obj_dir

        #Next move if you aren't blocked or take note of who got blocked
        #queue tracks the blocked ants?
        #G: Yup, and we keep popping stuff off the queue until it is empty or unchanging
        for id_num in range(1, num_ants+1):
            #print 'Ant number ' + str(id_num) + ' voted to go: ' + str(ant_dict[id_num].vote)
            env, queue = actuate_movement(env, ant_dict[id_num], trans_obj, queue, id_num)

        #print 'Waiting to move: ' + str(queue) #(Removed by Jessie)
        #Now blocked people move until all that are left are ants that can't move
        base_q_len = len(queue)
        update_q_len = 0
        temp_queue = []
        while (base_q_len != update_q_len):
            base_q_len = len(queue)

            for id_num in queue:
                env, temp_queue = actuate_movement(env, ant_dict[id_num], trans_obj, temp_queue, id_num)

            update_q_len = len(temp_queue)
            queue = temp_queue
            temp_queue = []

        env = actuate_object_movement(env, trans_obj, ant_dict, obj_mark_num)

        #Fast but shitty vis
        ascii_vis(env,obj_mark_num)
        sleep(.1)

        #Fancy but slow visual
        # cMap = []
        # for value, colour in zip([0,1,2,3],["White", "DarkBlue", "LightBlue", "Red"]):
        #     cMap.append((value/3.0, colour))

        # custom_cmap = LinearSegmentedColormap.from_list("custom", cMap)

        # plt.imshow(vis_env_mapping(env,obj_mark_num), cmap=custom_cmap, interpolation='nearest')
        # plt.title('Radius:' + str(radius) + ' Time: ' + str(time) + ' Num_ants: ' + str(num_ants) + ' Grad size: ' + str(m) + ' x ' + str(m))
        # plt.pause(0.1)
        # plt.savefig('../simulation/simulation' + str(time) + '.png')

    # plt.show()

    #Repeat


if __name__ == "__main__":
    random_pos = 0
    m = 20
    num_ants = 80
    radius = 5
    obj_size = 1
    obj_mark_num = 5000
    volunteer_prob = .01

    main(m, num_ants, random_pos, radius, obj_size, obj_mark_num,volunteer_prob)
