import numpy as np
from scipy import optimize

from self_equilibrium.static_analysis import zero_displacement


def get_self_stress_matrix(arch, tie, nodes, hangers, factors=None):
    n = 2 + len(hangers.get_hanger_forces(i=0))
    x = [0 for i in range(n)]
    b = moment_distribution(x, hangers, arch, tie, nodes, factors=factors)
    a = []
    for i in range(n):
        x[i] = 1
        a_i = moment_distribution(x, hangers, arch, tie, nodes, factors=factors) - b
        a.append(list(a_i))
        x[i] = 0
    a = np.array(a).transpose()
    return a, b


def moment_distribution(x, hangers, arch, tie, nodes, factors=None):
    hangers.set_prestressing_forces(x[2:])
    arch.assign_permanent_effects(nodes, hangers, x[0], -x[1])
    tie.assign_permanent_effects(nodes, hangers, -x[0], x[1])
    moment_arch = arch.effects['Permanent']['Moment']
    moment_tie = tie.effects['Permanent']['Moment']
    if factors:
        moment_arch *= factors[0]
        moment_tie *= factors[1]
    result_array = np.concatenate((moment_arch, moment_tie))
    return result_array


def blennerhassett_forces(arch, tie, nodes, hangers):
    forces = np.array([2420, 2015, 2126, 2051, 1766, 1931, 1877, 1784, 1757, 1646, 1601, 2371, 1842])

    a, b = get_self_stress_matrix(arch, tie, nodes, hangers)
    mod = np.zeros((a.shape[1], 3))
    mod[0, 0] = 1
    mod[1, 1] = 1
    mod[2:, 2] = forces
    ones = np.ones_like(np.expand_dims(b, axis=1))
    a_ub = np.vstack((np.hstack((-ones, -a @ mod)), np.hstack((-ones, a @ mod))))
    b_ub = np.array(list(b) + list(-b))
    c = np.array([1] + [0 for i in range(3)])
    bounds = [(-np.inf, np.inf) for i in range(3)] + [(0.8, 1.2)]
    sol = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='revised simplex')  # , x0=x0)
    x = sol.x

    hangers.set_prestressing_forces(list(x[3] * forces))
    hangers.assign_permanent_effects()
    arch.assign_permanent_effects(nodes, hangers, x[1], -x[2])
    tie.assign_permanent_effects(nodes, hangers, -x[1], x[2])
    return


def optimize_self_stresses(arch, tie, nodes, hangers):
    a, b = get_self_stress_matrix(arch, tie, nodes, hangers, factors=[1, 1.5])
    ones = np.ones_like(np.expand_dims(b, axis=1))
    a_ub = np.vstack((np.hstack((-ones, -a)), np.hstack((-ones, a))))
    b_ub = np.array(list(b) + list(-b))
    c = np.array([1] + [0 for i in range(a.shape[1])])

    zero_displacement(tie, nodes, hangers, dof_rz=True)
    hanger_forces = hangers.get_hanger_forces(i=0)
    bounds = [(-np.inf, np.inf) for i in range(3)] + [(0.8 * force, 1.2 * force) for force in hanger_forces]
    sol = optimize.linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method='revised simplex')  # , x0=x0)
    x = sol.x

    hangers.set_prestressing_forces(x[3:])
    hangers.assign_permanent_effects()
    arch.assign_permanent_effects(nodes, hangers, x[1], -x[2])
    tie.assign_permanent_effects(nodes, hangers, -x[1], x[2])
    return
