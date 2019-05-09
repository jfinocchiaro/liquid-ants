import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # to_plot = np.load('../data/no_huddle/num_exp_10/objsize1_numexp10_timelimit1500_m25.npy')
    to_plot = np.load('../data/no_huddle/num_exp_25/objsize1_numexp25_timelimit3000_m25.npy')

    # print(to_plot.shape)
    # print(to_plot_too.shape)



    np.clip(to_plot,0,1501,out=to_plot)
    # to_plot = np.concatenate((to_plot, to_plot_too), axis=2)

    # print(to_plot.shape)

    mean = np.mean(to_plot, axis = 2)
    # varience = np.var(to_plot, axis = 2)
    # std = np.std(to_plot, axis = 2)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    mappable = ax.imshow(mean, origin='lower', cmap = 'jet')
    ax.xaxis.set_ticks_position('bottom')

    ax.set_title('Average of Runtime over $25$ simulations on $25$ by $25$ lattice', fontsize=22)
    ax.set_xlabel('Number of agents', fontsize=18)
    ax.set_ylabel('r', fontsize=18)

    ax.set_xticklabels([1,1,5,10,15,20,25])
    # ax.set_yticklabels([1,25])

    fig.colorbar(mappable)

    plt.show()