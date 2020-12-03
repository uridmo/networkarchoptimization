import pickle
import tracemalloc

from bridges.Blennerhassett import BlennerhassettBridge
from plotting.adjustments import adjust_overview_plots, adjust_small_plots
from plotting.colors import colors
from plotting.save import save_plot

tracemalloc.start()

bridge_ref = BlennerhassettBridge(exact_cross_sections=True, self_stress_state='Zero-displacement')
bridge_ref.plot_elements()

fig = bridge_ref.plot_all_effects('Permanent', label='Reference calculation', c=colors[0])

# Plot ranges from design drawings
axs = fig.get_axes()
axs[0].axhline(-44.5, c=colors[1], lw=1)
axs[0].axhline(-38, c=colors[1], lw=1)
axs[1].axhline(36, c=colors[1], lw=1)
axs[1].axhline(34.5, c=colors[1], lw=1)
axs[2].axhline(2.420/3.4, c=colors[1], lw=1)
axs[2].axhline(1.600/3.4, c=colors[1], lw=1)
axs[3].axhline(3.69, c=colors[1], lw=1)
axs[3].axhline(-3.69, c=colors[1], lw=1)
axs[4].axhline(2.7, c=colors[1], lw=1)
axs[4].plot([0, 270], [-3.17, -3.17], label='Design drawings', c=colors[1], lw=1)

adjust_overview_plots(fig)
save_plot(fig, 'base case', 'Permanent state')

fig = bridge_ref.plot_effects('LL', 'Moment', label='Reference calculation range', c=colors[0])

axs = fig.get_axes()
hanger_forces = [0.4981984, 0.7517458, 0.7695386, 0.7295048, 0.6850228, 0.644989, 0.5827142, 0.5515768, 0.5070948,
                 0.467061, 0.4136826, 0.3603042, 0.3514078]
hanger_forces = [hanger_force / 3.4 for hanger_force in hanger_forces]
hanger_x = [267.8*(i+1)/14 for i in range(13)]
axs[0].plot([0, 270], [0.744, 0.744], label='Design drawings', c=colors[1], lw=1)
axs[1].plot([0, 270], [4.73, 4.73], label='Design drawings', c=colors[1], lw=1)
axs[2].plot(hanger_x, hanger_forces, label='Design drawings', c=colors[1])

adjust_small_plots(fig)
save_plot(fig, 'base case', 'Live load')

bridge_ref.cross_section_table(slice(0, 4), slice(0, 4), 'ULS Overview Tables', 'Final Design')

# Save the demand over capacity ratios of the reference case
dc = []
arch_cs = bridge_ref.arch_cross_sections[1:4]
tie_cs = bridge_ref.tie_cross_sections[1:4]
hanger_cs = [bridge_ref.hangers_cross_section]
cross_sections = arch_cs + tie_cs + hanger_cs
for cs in cross_sections:
    dc.append(cs.max_doc())
f = open('base case/dc_ratios.pckl', 'wb')
pickle.dump(dc, f)
f.close()

# Evaluate the cost function
a = bridge_ref.cost_function()
print('Costs: $', round(a/1000)/1000, 'Mio.')


current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
tracemalloc.stop()
