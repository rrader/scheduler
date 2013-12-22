import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def new_node():
    return {"weight": 2}


def draw(plan_task, plan_copy, tasks, time, cpus):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for x in range(1, cpus+1):
        rang = []
        for t in [t for t in plan_task if t[1] == x]:
            rang.append((t[2], tasks[t[0]]))
            plt.annotate(t[0]+1, (t[2] + 0.1, x + 0.2))
        ax.broken_barh(rang, (x, 0.5), facecolors='lightgray')

    for x in range(1, cpus+1):
        rang = []
        for t in plan_copy[x-1]:
            rang.append((t[0], t[1] - t[0]))
            plt.annotate("{}>\n{}".format(t[2], t[3]), (t[0] + 0.1, x + 0.6))
        ax.broken_barh(rang, (x+0.5, 0.5), facecolors='yellow')

    #ax.broken_barh([ (10, 50), (100, 20),  (130, 10)] , (20, 9),
    #                facecolors=('red', 'yellow', 'green'))
    ax.set_ylim(1, cpus+1)
    ax.set_xlim(0, time)
    ax.set_xlabel('seconds since start')
    ax.set_yticks(list(range(1, cpus+1)))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(5))
    #plt.xticks(range(1, time + 30))
    #ax.set_yticklabels(['Bill', 'Jim'])
    ax.grid(True, which="both")
    #ax.annotate('race interrupted', (61, 25),
    #            xytext=(0.8, 0.9), textcoords='axes fraction',
    #            arrowprops=dict(facecolor='black', shrink=0.05),
    #            fontsize=16,
    #            horizontalalignment='right', verticalalignment='top')
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.show()
