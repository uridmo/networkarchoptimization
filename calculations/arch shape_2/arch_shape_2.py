import numpy as np
from matplotlib import pyplot

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_plot
from plotting.plots import arch_or_tie_plots
from plotting.general import colors

cable_loss = False
arch_shape = 'Continuous optimisation'

bridge_85 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                 hanger_params=(np.radians(85),))

bridge_65 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                 hanger_params=(np.radians(65),))

bridge_45 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                 hanger_params=(np.radians(45),))

bridge_85_45 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                    hanger_arrangement='Constant Change', hanger_params=(np.radians(85),np.radians(65)))

bridge_r35 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                  hanger_arrangement='Radial', hanger_params=(np.radians(35), ))

bridge_r25 = BlennerhassettBridge(arch_optimisation=False, arch_shape=arch_shape, cable_loss=cable_loss,
                                  hanger_arrangement='Radial', hanger_params=(np.radians(25), ))

bridges_dict = {'85° Arrangement': bridge_85,
                '65° Arrangement': bridge_65,
                '45° Arrangement': bridge_45,
                '85° - 45° Arrangement': bridge_85_45,
                '35° Radial Arrangement': bridge_r35,
                '25° Radial Arrangement': bridge_r25
                }

span = 267.8
rise = 53.5
fig, axs = pyplot.subplots(1, 2, figsize=(8, 2), dpi=240)
for i, key in enumerate(bridges_dict):
    bridge = bridges_dict[key]
    nodes = bridge.network_arch.arch.nodes
    x = np.array([node.x for node in nodes])
    y = np.array([node.y for node in nodes])
    y_ref = [rise * (1 - ((x_i - span / 2) / (span / 2)) ** 2) for x_i in x]
    axs[0].plot(x, y-y_ref, label=key, c=colors[i], lw=0.7)

# y = np.array([rise - radius * (1 - (1 - ((x_i - span / 2) / radius) ** 2) ** 0.5) for x_i in x])
# axs[0].plot(x, y-y_ref, label='Circular arch', c=colors[i+1], lw=0.7)

axs[0].set_title('Arch shape')
axs[0].set_ylabel('Deviation [m]')
adjust_plot(axs[0], step=0.2, min_0=True)

axs[1].remove()
handles, labels = axs[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.85), frameon=False)
fig.savefig('arch_shapes_2.png')
pyplot.show()
