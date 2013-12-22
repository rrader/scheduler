from graph import draw


def start_nodes(conn):
    z = []
    for i, v in enumerate(conn.T):
        if v.sum() == 0:
            z.append(i)
    return z


def split_levels(_conn):
    conn = _conn.copy()
    sn = start_nodes(conn)
    processed = sn[:]
    levels = [sn]
    while len(sn) > 0:
        conn[processed, :] = 0
        sn = start_nodes(conn)
        for i in processed:
            sn.remove(i)
        levels.append(sn)
        processed += sn
    return levels

def find_paths(conn, sn=None, history=None):
    paths = []
    where_to = []
    if sn is None:
        sn = start_nodes(conn)
        for i in sn:
            paths += find_paths(conn, sn=i, history=[])
        return paths
    for i, nx in enumerate(conn[sn, :]):
        if nx > 0:
            paths += find_paths(conn, sn=i, history=history+[sn])
    if conn[sn, :].sum() == 0:
        return [history + [sn]]
    return paths

def weight_paths(conn, tasks):
    paths = find_paths(conn)
    def weigth(path):
        node_w = [tasks[node] for node in path]
        transfer_w = [conn[t] for t in zip(path, path[1:])]
        return sum(node_w) + sum(transfer_w)
    weigths = [(weigth(path), path) for path in paths]
    return sorted(weigths, key=lambda x: x[0], reverse=True)

def find_critical_path(conn, nodes):
    return weight_paths(conn, nodes)[0][1]

def is_sublist(sublist, suplist):
    return all(i in suplist for i in sublist)

def pop_priorities(lst, priorities):
    for p in priorities:
        if p in lst:
            lst.remove(p)
            return p
    return lst.pop()

def schedule(conn, tasks, cpus):
    tasks_list = tasks.copy()
    levels = split_levels(conn)
    cp = find_critical_path(conn, tasks)  # fixme: iterate and check all pathes
    print(cp, "<< critical path")

    plan_task = [[i, None, None] for i, _ in enumerate(tasks)]  # (task, cpu, time)
    plan_copy = [[] for i in range(cpus)]  # (task, cpu, time)

    def data_ready(task):
        return plan_task[task][2] + tasks[task]

    def get_ready(time):
        """ List ready tasks (without data transfer)"""
        ready = list(set([t[0] for t in plan_task if t[1] is not None and (time >= t[2] + tasks[t[0]])]))
        return ready

    def get_ready_cpus(time):
        """ List free cpus """
        cpus_lst = list(range(1, cpus+1))
        for t in plan_task:
            if t[1] and (t[2] <= time < (t[2] + tasks[t[0]])):
                cpus_lst.remove(t[1])
        return cpus_lst

    def get_dependencies(task):
        return [i for i, v in enumerate(conn[:, task]) if v > 0]

    def get_calculated(time):
        ready = get_ready(time)
        return [t for t in range(len(tasks)) if is_sublist(get_dependencies(t), ready)]

    def get_ready_to_plan(time):
        ready = get_calculated(time)
        return ready

    def is_planned(task):
        return any(i[0] == task and i[1] is not None for i in plan_task)

    def not_planned(tasks):
        return [int(t) for t in tasks if not is_planned(t)]

    def get_dependents(task):
        return [i for i, v in enumerate(conn[task]) if v > 0]
    ## copy 1) to node in highest level, 2) time to execute is lowest

    def do_plan_copy(time, list):
        pass

    ################################################
    #time = 0
    #while not_planned(range(len(tasks))):
    ##for _ in range(9):
    #    ready = get_ready(time)
    #    ready_cpus = get_ready_cpus(time)
    #    not_planned_list = not_planned(get_ready_to_plan(time))
    #    for r in not_planned_list:
    #        print("Planning %d" % r)
    #        if not ready_cpus:
    #            break
    #        plan_task[r][1] = ready_cpus.pop()
    #        for d in get_dependencies(r):
    #            copies = []
    #            if plan_task[r][1] != plan_task[d][1]:
    #                copies.append(plan_task[d][1], plan_task[r][1])
    #            do_plan_copy(time, copies)
    #        plan_task[r][2] = time
    #    else:
    #        time += 1
    #        continue
    #
    #    if not ready_cpus:
    #        time += 1
    #draw(plan_task, tasks, time+10, cpus)

    def is_busy_with_copying(time, cpu):
        return any(p[0] <= time < p[1] for p in plan_copy[cpu-1])

    def nearest_copy_ability(time, cpu, w):
        ts = int(time)
        while not all(not is_busy_with_copying(t, cpu) for t in range(ts, ts+int(w))):  # can be better, +1?
            ts += 1
        return ts

    time = 0
    while not_planned(range(len(tasks))):
        ready = get_ready(time)
        ready_cpus = get_ready_cpus(time)
        able_to_plan = not_planned(get_ready_to_plan(time))
        if not able_to_plan:
            time += 1
            continue
        for r in able_to_plan:
            if not ready_cpus:
                time += 1
                break
            weigths = sorted([(d, conn[d, r]) for d in get_dependencies(r)],
                             key=lambda x: x[1], reverse=True)
            preferred_cpus = [plan_task[i][1] for i, w in weigths]
            # sort weights
            print(r+1, get_dependencies(r), weigths, preferred_cpus, ready_cpus)
            if preferred_cpus:
                # TODO: look forward on data copy length time
                cpu = pop_priorities(ready_cpus, preferred_cpus)
            else:
                cpu = ready_cpus.pop()
            # copy
            time_added = [time]
            plans = []
            for d, w in weigths:
                d_cpu = plan_task[d][1]
                if d_cpu == cpu: continue
                time_start = plan_task[d][2] + tasks[d]
                mc1 = nearest_copy_ability(time_start, cpu, w)
                mc2 = nearest_copy_ability(time_start, d_cpu, w)
                plan = max(mc1, mc2)
                plans.append((d, w, time_start))

            for d, w, time_start in sorted(plans, key=lambda x:x[2]):
                d_cpu = plan_task[d][1]
                mc1 = nearest_copy_ability(time_start, cpu, w)
                mc2 = nearest_copy_ability(time_start, d_cpu, w)
                plan = max(mc1, mc2)
                while mc1 != mc2:
                    mc1 = nearest_copy_ability(plan, cpu, w)
                    mc2 = nearest_copy_ability(plan, d_cpu, w)
                    plan = max(mc1, mc2)
                plan_copy[cpu-1].append((plan, plan + w, d+1, r+1))
                plan_copy[d_cpu-1].append((plan, plan + w, d+1, r+1))
                time_added.append(plan + w)
            # task
            plan_task[r][1] = cpu
            plan_task[r][2] = max(time_added)
        #break
    draw(plan_task, plan_copy, tasks, time+10, cpus)
