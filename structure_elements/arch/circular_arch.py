import numpy as np

from structure_elements.arch.arch import Arch


class CircularArch(Arch):
    def __init__(self, nodes, span, rise, n=100):
        super().__init__(nodes, span, rise)

        radius = (rise ** 2 + (span / 2) ** 2) / (2 * rise)
        x_arch = list(np.linspace(0, span, 2 * n + 1))
        y_arch = [rise - radius * (1 - (1 - ((x - span / 2) / radius) ** 2) ** 0.5) for x in x_arch]

        for i in range(len(x_arch)):
            self.insert_node(nodes, x_arch[i], y_arch[i])
        return
