import numpy as np

from structureanalysis import structure_analysis
from structureanalysis import verify_input
from structureanalysis.plotting.plot_loads import plot_loads
from structureanalysis.plotting.plot_internal_forces import plot_internal_forces


def assign_hanger_forces_zero_displacement(tie, nodes, dof_rz=False):
    n = len(tie.nodes)
    nodes_location = [node.coordinates() for node in nodes]
    structural_nodes = {'Location': nodes_location}

    beams_nodes, beams_stiffness = tie.get_beams()
    beams = {'Nodes': beams_nodes, 'Stiffness': beams_stiffness}

    load_distributed = tie.self_weight_loads()
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
    d_tie, if_tie, rd_tie = structure_analysis(model, discType='Lengthwise', discLength=1)

    plot_loads(model, 0, 'Hello')
    plot_internal_forces(model, d_tie, if_tie, 0, 'Moment', 'Hello 2')

    mz_0 = if_tie[0]['Moment'][0][0]
    node_forces = [rd[2] for rd in rd_tie[0][2:]]
    node_forces2hanger_forces_equal(node_forces, tie)
    return mz_0


def node_forces2hanger_forces_equal(node_forces, tie):
    for i in range(len(node_forces)):
        sinus_sum = 0
        for hanger in tie.hanger_group[i]:
            sinus_sum += np.sin(hanger.inclination)
        hanger_force = node_forces[i] / sinus_sum
        for hanger in tie.hanger_group[i]:
            hanger.prestressing_force = hanger_force
    return
