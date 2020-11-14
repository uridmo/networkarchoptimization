import numpy as np

from plotting.model import plot_model
from plotting.save import save_plot
from structure_analysis import structure_analysis
from structure_analysis import verify_input


def zero_displacement(tie, nodes, dof_rz=False, plot=False):
    structural_nodes = nodes.structural_nodes()
    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}
    load_distributed = tie.self_weight()
    load_group = {'Distributed': load_distributed}
    loads = [load_group]
    restricted_degrees = [[tie.start_node.index, 1, 1, int(dof_rz), 0]]
    restricted_degrees += [[tie.end_node.index, 1, 1, int(dof_rz), 0]]
    for node in tie.nodes[1:-1]:
        restricted_degrees += [[node.index, 0, 1, 0, 0]]
    boundary_conditions = {'Restricted Degrees': restricted_degrees}
    model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
             'Boundary Conditions': boundary_conditions}

    verify_input(model)
    d_tie, if_tie, rd_tie = structure_analysis(model)
    mz_0 = if_tie[0]['Moment'][0][0] if dof_rz else 0

    # Assign the support reaction forces to the hangers
    node_forces = [rd[2] for rd in rd_tie[0][2:]]
    node_forces2hanger_forces_equal(node_forces, tie)

    if plot:
        # Adapt loads to have a nice plot
        load_distributed = load_distributed[0]
        load_distributed[2] = tie.end_node.x
        load_group = {'Distributed': [load_distributed]}
        loads = [load_group]
        model = {'Nodes': structural_nodes, 'Beams': beams, 'Loads': loads,
                 'Boundary Conditions': boundary_conditions}

        fig, ax = plot_model(model, tie)
        save_plot(fig, 'Models', 'Hanger Forces')
    return mz_0


def node_forces2hanger_forces_equal(node_forces, tie):
    j = 0
    for i in range(len(node_forces)):
        while not tie.hangers[j]:
            j += 1
        sinus_sum = 0
        for hanger in tie.hangers[i + 1]:
            sinus_sum += np.sin(hanger.inclination)
        hanger_force = node_forces[i] / sinus_sum
        for hanger in tie.hangers[i + 1]:
            hanger.prestressing_force = hanger_force
        j += 1
    return
