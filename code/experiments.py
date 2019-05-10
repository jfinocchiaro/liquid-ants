import driver as dr
import numpy as np

def main():
    m_max = 25
    obj_size = 1
    default_radius = 5
    default_num_agents = 20
    default_vol_prob = 0.01
    TIME_LIMIT = 1500
    num_exp = 40

    ms = np.linspace(10, m_max ,m_max+1-10, endpoint=True, dtype=int)
    radii = np.linspace(1,m_max,m_max+1, endpoint=True, dtype=int)
    #num_agents = np.array([1, 3, 5, 7])
    num_agents = np.linspace(1,m_max,m_max, endpoint=True, dtype = int)
    probabilities = np.linspace(0,1,20, endpoint=False)

    m=m_max

    # time_results = np.zeros((radii.size, num_agents.size, num_exp))
    # for i in range(radii.size):
    #     for j in range(num_agents.size):
    #         for k in range(num_exp):
    #             t = dr.main(m, num_agents[j], 0, radii[i], 1, 5000, default_vol_prob, TIME_LIMIT = TIME_LIMIT)
    #             time_results[i,j,k] = t
    #             print 'Time ' + str(t) + ' radius ' + str(radii[i]) + ' num_agents ' + str(num_agents[j])
    # for i in range(num_exp):
    #     print time_results[:,:,i]

    # print '~~~~~~~~~~~~~~~~~~~~~~~~~~'
    # print np.mean(time_results, axis = 2)

    # filename = 'objsize' + str(obj_size) + '_numexp' + str(num_exp) + '_timelimit' + str(TIME_LIMIT) + '_m' + str(m)
    # np.save(filename, time_results)

    probability_results = np.zeros([probabilities.size,num_exp])
    for i in range(probabilities.size):
        for k in range(num_exp):
            t = dr.main(m, m, 0, 4, 1, 5000, probabilities[i], TIME_LIMIT = TIME_LIMIT)
            probability_results[i,k] = t
            print 'Time ' + str(t) + ' prob ' + str(probabilities[i])
    for i in range(num_exp):
        print probability_results[:,i]

    print '~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print np.mean(probability_results, axis = 1)

    filename = 'probability_results_objsize' + str(obj_size) + '_numexp' + str(num_exp) + '_timelimit' + str(TIME_LIMIT) + '_m' + str(m) + '_r' + str(4)
    np.save(filename, probability_results)





if __name__ == '__main__':
    main()
