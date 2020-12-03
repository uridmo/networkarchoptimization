import pickle

import numpy as np

from bridges.bridge import Bridge
from structure_elements.cross_section import CrossSection


class BlennerhassettBridge(Bridge):
    def __init__(self, span=267.8, rise=53.5, n_cross_girders=13, g_deck=115.3, g_utilities=35.1, n_hangers=13,
                 hanger_arrangement='Parallel', hanger_params=(1.0646,), qd_live_load=27, qc_live_load=325,
                 arch_shape='Parabolic', arch_optimisation=False, self_stress_state='Overall-optimisation',
                 self_stress_state_params=((0.75, 1.4),), exact_cross_sections=False, knuckles=True):

        resistance_arch_1 = [130000, 78708, 79115]
        resistance_arch_2 = [108768, 71458, 63445]
        resistance_arch_3 = [82309, 50017, 42729]
        resistance_tie_1 = [153228, 100810, 76190]
        resistance_tie_2 = [117134, 82766, 56610]
        resistance_tie_3 = [100574, 76175, 45792]
        resistance_hanger = [n_hangers/13*3400, 1, 1]

        stiffness_arch_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_arch_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_arch_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_tie_1 = [77429 * 10 ** 3, 31473 * 10 ** 3]
        stiffness_tie_2 = [65997 * 10 ** 3, 28673 * 10 ** 3]
        stiffness_tie_3 = [61814 * 10 ** 3, 28113 * 10 ** 3]
        stiffness_hanger = [n_hangers/13*643.5 * 10 ** 3, 10 ** 6]

        wind_load_arch_1 = {'Normal Force': [-8175], 'Moment': [668], 'Moment y': [13851]}
        wind_load_arch_2 = {'Normal Force': [-7793], 'Moment': [-670], 'Moment y': [10749]}
        wind_load_arch_3 = {'Normal Force': [-4066], 'Moment': [-533], 'Moment y': [2591]}
        wind_load_arch_4 = {'Normal Force': [-3852], 'Moment': [117], 'Moment y': [111]}
        wind_load_tie_1 = {'Normal Force': [5369], 'Moment': [-2327], 'Moment y': [9653]}
        wind_load_tie_2 = {'Normal Force': [7002], 'Moment': [-1109], 'Moment y': [5880]}
        wind_load_tie_3 = {'Normal Force': [6152], 'Moment': [404], 'Moment y': [434]}
        wind_load_tie_4 = {'Normal Force': [5275], 'Moment': [702], 'Moment y': [788]}
        wind_load_hangers = {'Normal Force': [480]}

        if exact_cross_sections:
            cs_tie_1 = CrossSection('Tie 1', 26.4, stiffness_tie_1, resistance_tie_1, wind_effects=wind_load_tie_1)
            cs_tie_2 = CrossSection('Tie 2', 26.4, stiffness_tie_2, resistance_tie_2, wind_effects=wind_load_tie_2)
            cs_tie_3 = CrossSection('Tie 3', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_3)
            cs_tie_4 = CrossSection('Tie 4', 26.4, stiffness_tie_3, resistance_tie_3, wind_effects=wind_load_tie_4)

            cs_tie = [cs_tie_1, cs_tie_2, cs_tie_3, cs_tie_4]
            cs_tie_x = [6.2, 34.8, 92.13]

            cs_arch_1 = CrossSection('Arch 1', 29.8, stiffness_arch_1, resistance_arch_1, wind_effects=wind_load_arch_1)
            cs_arch_2 = CrossSection('Arch 2', 29.8, stiffness_arch_2, resistance_arch_2, wind_effects=wind_load_arch_2)
            cs_arch_3 = CrossSection('Arch 3', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_3)
            cs_arch_4 = CrossSection('Arch 4', 29.8, stiffness_arch_3, resistance_arch_3, wind_effects=wind_load_arch_4)

            cs_arch = [cs_arch_1, cs_arch_2, cs_arch_3, cs_arch_4]
            cs_arch_x = [3.8, 28.8, 83.91]

            cs_hangers = CrossSection('Hanger', 0, stiffness_hanger, resistance_hanger, wind_effects=wind_load_hangers)
        else:
            raise Exception('Not defined yet.')

        cs_tie = cs_tie + cs_tie[-2::-1]
        cs_tie_x = cs_tie_x + [-x for x in cs_tie_x[::-1]]
        cs_arch = cs_arch + cs_arch[-2::-1]
        cs_arch_x = cs_arch_x + [-x for x in cs_arch_x[::-1]]

        if knuckles:
            cs_knuckle = CrossSection('Knuckle', 0, [28452 * 10 ** 3, 32380 * 10 ** 3], [1, 1, 1])
            knuckle_x = 4.1
            knuckle_inclination = np.radians(110)
            knuckle = (cs_knuckle, knuckle_x, knuckle_inclination)
        else:
            knuckle = ()

        super().__init__(span, rise, n_cross_girders, g_deck, g_utilities, qd_live_load, qc_live_load, arch_shape,
                         arch_optimisation, self_stress_state, self_stress_state_params, cs_arch_x, cs_arch, cs_tie_x,
                         cs_tie, n_hangers, hanger_arrangement, hanger_params, cs_hangers, knuckle)
        return

    def cost_function(self):

        unit_weight_arch_1 = 2467.05
        unit_weight_arch_2 = 2310.68
        unit_weight_arch_3 = 2310.68
        unit_weight_tie_1 = 2334.10
        unit_weight_tie_2 = 2008.71
        unit_weight_tie_3 = 2008.71

        unit_weight_hanger = 31.9 * 13 / self.hangers_amount
        unit_weight_anchorages = 2322.82 * 13 / self.hangers_amount

        unit_price_arch = 4
        unit_price_tie = 3.5
        unit_price_hanger = 22
        unit_price_anchorages = 9

        f = open('Base case/store.pckl', 'rb')
        dc = pickle.load(f)
        dc_arch_1_ref, dc_arch_2_ref, dc_arch_3_ref = dc[0], dc[1], dc[2]
        dc_tie_1_ref, dc_tie_2_ref, dc_tie_3_ref, dc_hangers_ref = dc[3], dc[4], dc[5], dc[6]

        arch_cs = self.arch_cross_sections
        arch_cs_1, arch_cs_2, arch_cs_3 = arch_cs[1], arch_cs[2], arch_cs[3]

        tie_cs = self.tie_cross_sections
        tie_cs_1, tie_cs_2, tie_cs_3 = tie_cs[1], tie_cs[2], tie_cs[3]

        hanger_cs = self.hangers_cross_section

        weight_arch_1 = 2*arch_cs_1.length * unit_weight_arch_1
        weight_arch_2 = 2*arch_cs_2.length * unit_weight_arch_2
        weight_arch_3 = 2*arch_cs_3.length * unit_weight_arch_3
        weight_tie_1 = 2*tie_cs_1.length * unit_weight_tie_1
        weight_tie_2 = 2*tie_cs_2.length * unit_weight_tie_2
        weight_tie_3 = 2*tie_cs_3.length * unit_weight_tie_3
        weight_hanger = 2*hanger_cs.length * unit_weight_hanger
        weight_anchorages = 2 * self.hangers_amount * unit_weight_anchorages

        cost_arch_1 = weight_arch_1 * unit_price_arch * arch_cs_1.max_doc() / dc_arch_1_ref
        cost_arch_2 = weight_arch_2 * unit_price_arch * arch_cs_2.max_doc() / dc_arch_2_ref
        cost_arch_3 = weight_arch_3 * unit_price_arch * arch_cs_3.max_doc() / dc_arch_3_ref

        cost_tie_1 = weight_tie_1 * unit_price_tie * tie_cs_1.max_doc() / dc_tie_1_ref
        cost_tie_2 = weight_tie_2 * unit_price_tie * tie_cs_2.max_doc() / dc_tie_2_ref
        cost_tie_3 = weight_tie_3 * unit_price_tie * tie_cs_3.max_doc() / dc_tie_3_ref

        cost_hanger = weight_hanger * unit_price_hanger * hanger_cs.max_doc() / dc_hangers_ref
        cost_anchorages = weight_anchorages * unit_price_anchorages * hanger_cs.max_doc() / dc_hangers_ref

        weights = [weight_arch_1, weight_arch_2, weight_arch_3, weight_tie_1, weight_tie_2, weight_tie_3, weight_hanger, weight_anchorages]
        weight = sum(weights)
        costs = [cost_arch_1, cost_arch_2, cost_arch_3, cost_tie_1, cost_tie_2, cost_tie_3, cost_hanger, cost_anchorages]
        cost = sum(costs) + 50000
        return cost