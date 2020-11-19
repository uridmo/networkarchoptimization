import numpy as np

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis
from structure_analysis import verify_input
from structure_elements.effects import min_multiple_lists, max_multiple_lists, connect_inner_lists
from scipy.optimize import minimize, Bounds


def optimize_self_stresses(arch, tie, nodes, hangers):
    def absolute_moment_minimum(x):
        hangers.set_hanger_forces(x[2:])
        arch.assign_permanent_effects(nodes, hangers, x[0], -x[1])
        tie.assign_permanent_effects(nodes, hangers, -x[0], x[1])
        moment_arch = connect_inner_lists(arch.effects['Permanent']['Moment'])
        moment_tie = connect_inner_lists(tie.effects['Permanent']['Moment'])
        result_array = moment_arch+moment_tie
        result = max(max(result_array), -min(result_array))
        print(result)
        return result

    mz_0 = zero_displacement(tie, nodes, hangers, dof_rz=True)
    n_0 = define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=-5 * 10 ** 3)
    hanger_forces = hangers.get_hanger_forces(i=0)
    x0 = [n_0, mz_0]+hanger_forces
    lb = [-np.inf, -np.inf] + [1.2 * force for force in hanger_forces]
    ub = [np.inf, np.inf] + [0.8 * force for force in hanger_forces]
    bounds = Bounds(lb, ub)
    sol = minimize(absolute_moment_minimum, x0, bounds=bounds, options={'maxiter': 1000, 'disp': True})
    x = sol.x
    hangers.set_hanger_forces(x[2:])
    hangers.assign_permanent_effects()
    arch.assign_permanent_effects(nodes, hangers, x[0], -x[1])
    tie.assign_permanent_effects(nodes, hangers, -x[0], x[1])
    return


def define_by_peak_moment(arch, nodes, hangers, mz_0, peak_moment=0):
    arch.assign_permanent_effects(nodes, hangers, 0, -mz_0)
    moments_arch = arch.effects['Permanent']['Moment']
    moment_max = max([max(moments) for moments in moments_arch])
    n_0 = (moment_max-peak_moment)/arch.rise
    return n_0


def zero_displacement(tie, nodes, hangers, dof_rz=False, plot=False):
    structural_nodes = nodes.structural_nodes()
    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    load_group = tie.self_weight()

    restricted_degrees = [[tie.nodes[0].index, 1, 1, int(dof_rz), 0]]
    restricted_degrees += [[tie.nodes[-1].index, 1, 1, int(dof_rz), 0]]
    for hanger in hangers:
        restricted_degrees += [[hanger.tie_node.index, 0, 1, 0, 0]]

    boundary_conditions = {'Restricted Degrees': restricted_degrees}
    model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': [load_group],
             'Boundary Conditions': boundary_conditions}

    verify_input(model)
    d_tie, if_tie, rd_tie = structure_analysis(model)
    mz_0 = if_tie[0]['Moment'][0][0] if dof_rz else 0

    # Assign the support reaction forces to the hangers
    nodes_x = [model['Nodes']['Location'][rd[0]][0] for rd in rd_tie[0][2:]]
    nodes_forces = [rd[2] for rd in rd_tie[0][2:]]
    # Assign the reaction forces to the hangers
    sine_proportional(nodes_x, nodes_forces, hangers)
    # sine_length_proportional(nodes_x, nodes_forces, hangers)

    if plot:
        # Adapt loads to have a nice plot
        load_distributed = load_group['Distributed'][0]
        load_distributed[2] = tie.span
        load_group = {'Distributed': [load_distributed]}
        loads = [load_group]
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        fig, ax = plot_model(model, tie)
        save_plot(fig, 'Models', 'Hanger Forces')
    return mz_0


def sine_proportional(nodes_x, nodes_forces, hangers):
    for i in range(len(nodes_forces)):
        sine_sum = 0
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                sine_sum += np.sin(hanger.inclination)
        hanger_force = nodes_forces[i] / sine_sum
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                hanger.prestressing_force = hanger_force
    return


def sine_length_proportional(nodes_x, nodes_forces, hangers):
    for i in range(len(nodes_forces)):
        sine_length_sum = 0
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                sine_length_sum += np.sin(hanger.inclination)**2 * hanger.length()
        hanger_force = nodes_forces[i] / sine_length_sum
        for hanger in hangers:
            if hanger.tie_node.x == nodes_x[i]:
                hanger.prestressing_force = hanger_force * np.sin(hanger.inclination) * hanger.length()
    return
