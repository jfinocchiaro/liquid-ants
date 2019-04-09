import numpy as np
from numpy.random import *
import ants_and_objects as a_o
from math import *
np.set_printoptions(suppress=True)

#TODO: fix hack of marking environment with addition of number
#TODO: make home base more than one tile
#TODO: Limit carrier ant's vision -- SEEMS DONE (Jessie)
#TODO: Currently gives vote to first agent with highest confidence. --SEEMS DONE (see line 179)
#TODO: Need to add some tie breaking scheme.
#TODO: Merge see_hb and move_towards_hb functions

#NOTE: Added action 'G' which means reached home and so "Go into the nest"
#NOTE: Made updating confidences second thing and merged it with broadcasting confidence
#NOTE: It's a square lattice now for simplicity of the 'physics'

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
            pos = (int(corner[0] + ((id_num-1) % row_length)), corner[1] + int((id_num-1) / row_length))
            ant_dict[id_num] = a_o.Ant(id_num, [], radius, 0, list(pos), choice(['N', 'S', 'E', 'W']), False)
            env[pos] = int(id_num)

        #place the object on top of the blob for now
        trans_obj = a_o.Transport(corner, [int(x + obj_size) for x in corner] , int(num_ants / 10)) #weight can change later
        for i in range(corner[0], corner[0]+ obj_size):
            for j in range(corner[1], corner[1]+ obj_size):
                ant_dict[env[(i,j)]].carrying = True
                ant_dict[env[(i,j)]].radius = 1 #if the ant is carrying the object, we want it to have vision radius.
                env[(i,j)] += int(obj_mark_num)

        #initialize home base. while loop makes sure that we don't start on home base because that's no fun
        in_obj = 1
        while (in_obj):
            hb_pos = (randint(0, m-1), randint(0, m-1))
            if (trans_obj.tl_position[0] <= hb_pos[0] <= trans_obj.br_position[0]) and (trans_obj.tl_position[1] <= hb_pos[1] <= trans_obj.br_position[1]):
                pass
            else:
                in_obj = 0

        env[hb_pos] = -100 #marking in environment where home base is.  by initialization, should have been 0 before.

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
                #this else is if we're on home base.
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
    if obj.tl_position[0] == m-obj_height-1:
        votes[1] = -1
    if obj.tl_position[1] == m-obj_width-1:
        votes[2] = -1



    max_vote = max(votes)
    winner = votes.index(max_vote)

    if winner == 0:
        obj.tl_position[0] = obj.tl_position[0]-1
        obj.br_position[0] = obj.br_position[0]-1
        return 'N'
    elif winner == 1:
        obj.tl_position[0] = obj.tl_position[0]+1
        obj.br_position[0] = obj.br_position[0]+1
        return 'S'
    elif winner == 2:
        obj.tl_position[1] = obj.tl_position[1]+1
        obj.br_position[1] = obj.br_position[1]+1
        return 'E'
    else:
        obj.tl_position[1] = obj.tl_position[1]-1
        obj.br_position[1] = obj.br_position[1]-1
        return 'W'

def main(m, num_ants, random_pos, radius, obj_size, obj_mark_num, volunteer_prob):
    env, ant_dict, trans_obj = initializeEnv(m, num_ants, random_pos, radius, obj_size, obj_mark_num)

    found_hb = False
    time = 0

    # Enter action sequence until home base is found.
    while(not found_hb):
        #Check if goal was reached
        for i in range(trans_obj.tl_position[0],trans_obj.br_position[0]+1):
            for j in range(trans_obj.tl_position[1],trans_obj.br_position[1]+1):
                if env[i,j] == -100:
                    found_hb = True
                    print "Simulation Complete after " + str(time) + " time steps."
                    print env
                    return 0
        time += 1
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        #if time == 2:
        #    quit()

        #Update action set by seeing who is in my radius
        for id_num in range(1, num_ants+1):
            ant_dict[id_num].action_set = ['N', 'S', 'E', 'W', 'G']

            for i in range(max(ant_dict[id_num].position[0]-ant_dict[id_num].radius,0),min(ant_dict[id_num].position[0]+ant_dict[id_num].radius,m-1)):
                for j in range(max(ant_dict[id_num].position[1]-ant_dict[id_num].radius,0),min(ant_dict[id_num].position[1]+ant_dict[id_num].radius,m-1)):
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
            else:
                queue.append(id_num)

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


        # what's the difference between this and the loop above, other than it being run over every ant this time?
        # Choose an action and broadcast it
        #for id_num in range(1, num_ants+1):  # (old implementation. replaced by for ant in sorted(...).)
        for ant in sorted(ant_dict.values(), key = lambda i: i.confidence, reverse = True):
            id_num = ant.id_num
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

        # Move in direction your vote went
        queue = [] #Who needs to move
        obj_queue = [] #Who is holding the object
        obj_direction_vote = [0,0,0,0] #Where do those people want to move

        #First update votes on others to votes on a direction
        for id_num in range(1, num_ants+1):
            while(ant_dict[id_num].vote not in ['N', 'S', 'E', 'W', 'G']):
                ant_dict[id_num].vote = ant_dict[ant_dict[id_num].vote].vote

        #Decide which way the object will move
        for id_num in range(1, num_ants+1):
            if ant_dict[id_num].carrying == True:
                obj_queue += [id_num]
                if ant_dict[id_num].vote == 'N':
                    obj_direction_vote[0] += 1
                elif ant_dict[id_num].vote == 'S':
                    obj_direction_vote[1] += 1
                elif ant_dict[id_num].vote == 'E':
                    obj_direction_vote[2] += 1
                elif ant_dict[id_num].vote == 'W':
                    obj_direction_vote[3] += 1
        obj_dir = tug_o_war(obj_direction_vote, trans_obj, m)
        for id_num in obj_queue:
            ant_dict[id_num].vote = obj_dir


        #Next move if you aren't blocked or take note of who got blocked
        #queue tracks the blocked ants?
        for id_num in range(1, num_ants+1):
            #print 'Ant number ' + str(id_num) + ' voted to go: ' + str(ant_dict[id_num].vote)
            if ant_dict[id_num].vote == 'N':
                try:
                    if env[ant_dict[id_num].position[0]-1,ant_dict[id_num].position[1]] > 0:
                        queue.append(id_num)
                        #print 'Added ant ' + str(id_num) + ' to the queue'
                        #print env
                    elif ant_dict[id_num].position[0]-1 < 0:
                        pass
                    else:
                        if env[ant_dict[id_num].position[0]-1, ant_dict[id_num].position[1]] != -100:
                            #print 'Ant number' + str(id_num)
                            #print env[tuple(ant_dict[id_num].position)]
                            env[tuple([ant_dict[id_num].position[0]-1, ant_dict[id_num].position[1]])] = env[tuple(ant_dict[id_num].position)]
                            #print ant_dict[id_num].position
                            env[tuple(ant_dict[id_num].position)] = 0
                            ant_dict[id_num].position[0] = ant_dict[id_num].position[0]-1
                except Exception as e:
                    print 'Ant number ' + str(id_num) + ' tried moving north but hit a wall'
                    print env
                    print e
                    #quit()

            elif ant_dict[id_num].vote == 'S':
                try:
                    if env[ant_dict[id_num].position[0]+1,ant_dict[id_num].position[1]] > 0:
                        queue.append(id_num)
                        #print 'Added ant ' + str(id_num) + ' to the queue'
                        #print env
                    elif ant_dict[id_num].position[0]+1 >= m:
                        pass
                    else:
                        if env[ant_dict[id_num].position[0]+1, ant_dict[id_num].position[1]] != -100:
                            #print 'Ant number' + str(id_num)
                            #print env[tuple(ant_dict[id_num].position)]
                            env[tuple([ant_dict[id_num].position[0]+1, ant_dict[id_num].position[1]])] = env[tuple(ant_dict[id_num].position)]
                            #print ant_dict[id_num].position
                            env[tuple(ant_dict[id_num].position)] = 0
                            ant_dict[id_num].position[0] = ant_dict[id_num].position[0]+1
                except Exception as e:
                    print 'Ant number ' + str(id_num) + ' tried moving south but hit a wall'
                    print env
                    print e
                    #quit()

            elif ant_dict[id_num].vote == 'E':
                try:
                    if env[ant_dict[id_num].position[0],ant_dict[id_num].position[1]+1] > 0:
                        queue.append(id_num)
                        #print 'Added ant ' + str(id_num) + ' to the queue'
                        #print env
                    elif ant_dict[id_num].position[1]+1 >= m:
                        pass
                    else:
                        if env[ant_dict[id_num].position[0], ant_dict[id_num].position[1]+1] != -100:
                            #print 'Ant number' + str(id_num)
                            #print env[tuple(ant_dict[id_num].position)]
                            env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]+1])] = env[tuple(ant_dict[id_num].position)]
                            env[tuple(ant_dict[id_num].position)] = 0
                            ant_dict[id_num].position[1] += 1
                except Exception as e:
                    print 'Ant number ' + str(id_num) + ' tried moving east but hit a wall'
                    print env
                    print e
                    #quit()

            elif ant_dict[id_num].vote == 'W':
                try:
                    if env[ant_dict[id_num].position[0],ant_dict[id_num].position[1]-1] > 0:
                        queue += [id_num]
                        #print 'Added ant ' + str(id_num) + ' to the queue'
                        #print env
                    elif ant_dict[id_num].position[1]-1 < 0:
                        pass
                    else:
                        if env[ant_dict[id_num].position[0], ant_dict[id_num].position[1]-1] != -100:
                            #print 'Ant number' + str(id_num)
                            #print env[tuple(ant_dict[id_num].position)]
                            env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]-1])] = env[tuple(ant_dict[id_num].position)]
                            #print ant_dict[id_num].position
                            env[tuple(ant_dict[id_num].position)] = 0
                            ant_dict[id_num].position[1] = ant_dict[id_num].position[1]-1
                except Exception as e:
                    print 'Ant number ' + str(id_num) + ' tried moving west but hit a wall'
                    print env
                    print e
                    #quit()


        print 'Waiting to move: ' + str(queue)
        #Now blocked people move until all that are left are ants that can't move
        base_q_len = len(queue)
        update_q_len = 0
        temp_queue = []
        while (base_q_len != update_q_len):
            base_q_len = len(queue)

            for id_num in queue:
                if ant_dict[id_num].vote == 'N':
                    if env[tuple([ant_dict[id_num].position[0]-1,ant_dict[id_num].position[1]])] > 0:
                        temp_queue.append(id_num)
                    elif ant_dict[id_num].position[0]-1 < 0:
                        pass
                    else:
                        if env[tuple([ant_dict[id_num].position[0]-1, ant_dict[id_num].position[1]])] != -100:
                            env[ant_dict[id_num].position[0]-1, ant_dict[id_num].position[1]] = env[tuple(ant_dict[id_num].position)]
                        env[tuple(ant_dict[id_num].position)] = 0
                        ant_dict[id_num].position[0] = ant_dict[id_num].position[0]-1

                elif ant_dict[id_num].vote == 'S':
                    if env[tuple([ant_dict[id_num].position[0]+1,ant_dict[id_num].position[1]])] > 0:
                        temp_queue.append(id_num)
                    elif ant_dict[id_num].position[0]+1 >= m:
                        pass
                    else:
                        if env[tuple([ant_dict[id_num].position[0]+1, ant_dict[id_num].position[1]])] != -100:
                            env[tuple([ant_dict[id_num].position[0]+1, ant_dict[id_num].position[1]])] = env[tuple(ant_dict[id_num].position)]
                        env[tuple(ant_dict[id_num].position)] = 0
                        ant_dict[id_num].position[0] = ant_dict[id_num].position[0]+1

                elif ant_dict[id_num].vote == 'E':
                    if env[tuple([ant_dict[id_num].position[0],ant_dict[id_num].position[1]+1])] > 0:
                        temp_queue.append(id_num)
                    elif ant_dict[id_num].position[1]+1 >= m:
                        pass
                    else:
                        if env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]+1])] != -100:
                            env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]+1])] = env[tuple(ant_dict[id_num].position)]
                        env[tuple(ant_dict[id_num].position)] = 0
                        ant_dict[id_num].position[1] = ant_dict[id_num].position[1]+1

                elif ant_dict[id_num].vote == 'W':
                    if env[tuple([ant_dict[id_num].position[0],ant_dict[id_num].position[1]-1])] > 0:
                        temp_queue.append(id_num)
                    elif ant_dict[id_num].position[1]-1 < 0:
                        pass
                    else:
                        if env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]-1])] != -100:
                            env[tuple([ant_dict[id_num].position[0], ant_dict[id_num].position[1]-1])] = env[tuple(ant_dict[id_num].position)]
                        env[tuple(ant_dict[id_num].position)] = 0
                        ant_dict[id_num].position[1] = ant_dict[id_num].position[1]-1

            update_q_len = len(temp_queue)
            queue = temp_queue
            temp_queue = []

        #Repeat
        print "Block 3"
        print env

if __name__ == "__main__":
    m = 10
    num_ants = 5
    random_pos = 0
    radius = 3
    obj_size = 1
    obj_mark_num = 5000
    volunteer_prob = .01

    main(m, num_ants, random_pos, radius, obj_size, obj_mark_num,volunteer_prob)
