import numpy as np
from matplotlib import pyplot


def adjust_overview_plots(fig):
    axs = fig.get_axes()

    axs[0].set_title('Arch')
    axs[0].set_ylabel('N [MN]')
    adjust_plot(axs[0])

    axs[1].set_title('Tie')
    adjust_plot(axs[1])

    axs[2].set_title('Hangers')
    axs[2].set_ylabel('D/C [-]')
    adjust_plot(axs[2], step=0.2, min_0=True)

    axs[3].set_ylabel('M [MNm]')
    adjust_plot(axs[3])

    adjust_plot(axs[4])

    axs[5].remove()
    handles, labels = axs[4].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.7, 0.45), frameon=False)
    pyplot.show()
    return


def adjust_small_plots(fig):
    axs = fig.get_axes()

    axs[0].set_title('Arch')
    axs[0].set_ylabel('M [MNm]')
    adjust_plot(axs[0])

    axs[1].set_title('Tie')
    adjust_plot(axs[1])

    axs[2].set_title('Hangers')
    axs[2].set_ylabel('D/C [-]')
    adjust_plot(axs[2], step=0.2, min_0=True)

    axs[3].remove()
    handles, labels = axs[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper left', bbox_to_anchor=(0.55, 0.45), frameon=False)

    pyplot.show()
    return


def adjust_plot(ax, step=1.0, min_0=False):
    ax.set_xlim([0, 270])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    y_ticks = ax.get_yticks()
    if not min_0:
        ax.set_ylim([np.floor(y_ticks[0] / step) * step, np.ceil(y_ticks[-1] / step) * step])
    else:
        ax.set_ylim([np.min([np.floor(y_ticks[0] / step) * step, 0]), np.ceil(y_ticks[-1] / step) * step])
    y_ticks = ax.get_yticks()
    # ax.set_ylim([y_ticks[0], y_ticks[-1]])
    # ax.set_yticks(y_ticks)
    ax.axhline(0, color='black', lw=0.5)
    return
