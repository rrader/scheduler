from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def new_node():
    return {"weight": 2}


def draw(plan_task, plan_copy, tasks, time, cpus, cp):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    print(plan_task)

    for x in range(1, cpus+1):
        rang = []
        rang_dups = []
        rang_cp = []
        for t in [t for t in plan_task if x in t[1]]:
            for i, cpu in enumerate(t[1]):
                if cpu == x:
                    if i == 0:
                        if t[0] in cp:
                            rang_cp.append((t[2][i], tasks[t[0]]))
                        else:
                            rang.append((t[2][i], tasks[t[0]]))
                    else:
                        rang_dups.append((t[2][i], tasks[t[0]]))
                    plt.annotate(t[0]+1, (t[2][i] + 0.1, x + 0.2))
        ax.broken_barh(rang, (x, 0.5), alpha=.5, facecolors='lightgray')
        ax.broken_barh(rang_dups, (x, 0.5), alpha=.5, facecolors='purple')
        ax.broken_barh(rang_cp, (x, 0.5), alpha=.5, facecolors='lightgray', hatch='/')

    for x in range(1, cpus+1):
        rang = []
        for t in plan_copy[x-1]:
            rang.append((t[0], t[1] - t[0]))
            plt.annotate("{}>\n{}".format(t[2], t[3]), (t[0] + 0.1, x + 0.6))
        ax.broken_barh(rang, (x+0.5, 0.5), facecolors='yellow')

    ax.set_ylim(1, cpus+1)
    ax.set_xlim(0, time)
    ax.set_xlabel('tacts since start')
    ax.set_yticks(list(range(1, cpus+1)))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(2))

    ax.grid(True, which="both")
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.legend([Rectangle((0, 0), 1, 1, fc="lightgray", hatch='/'),
                Rectangle((0, 0), 1, 1, fc="lightgray"),
                Rectangle((0, 0), 1, 1, fc="purple"),
                Rectangle((0, 0), 1, 1, fc="yellow")],
               ["Critical Path",
                "Regular tasks",
                "Duplicated tasks",
                "Data transfer in switch"])
    plt.show()
