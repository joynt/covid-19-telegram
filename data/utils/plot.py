import matplotlib.pyplot as plt
import numpy as np

def trim_axs(axs, N):
    """little helper to massage the axs list to have correct length..."""
    axs = axs.flat
    for ax in axs[N:]:
        ax.remove()
    return axs[:N]

def plot_cases(confirmed, align_indexes, align_around, path):
    # Simple graph

    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(20, 10))
    ax = trim_axs(ax, 6)
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[0].plot(v, label=c, linewidth=linewidth)

    ax[0].legend(loc="upper left")
    ax[0].set_title("Number of cases", fontsize=14, fontweight='bold')
    ax[0].set_xlabel(f"Days since February 22 2020")
    ax[0].grid()

    # Simple aligned
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[1].plot(v[align_indexes[c]:], label=c, linewidth=linewidth)

    ax[1].legend(loc="upper left")
    ax[1].set_title("Number of cases", fontsize=14, fontweight='bold')
    ax[1].set_xlabel(f"Days since cases are around {align_around}")
    ax[1].grid()

    # Logarithm Gradient
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        array = np.array(v)
        log_array = np.log10(array+1)
        array = np.gradient(log_array)
        ax[2].plot(array, label=c, linewidth=linewidth)

    ax[2].legend(loc="upper left")
    ax[2].set_title("Gradient of number of cases in log scale", fontsize=14, fontweight='bold')
    ax[2].set_xlabel(f"Days since February 22 2020")
    ax[2].grid()

    # Logarithm
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        array = np.array(v)
        ax[3].plot(np.log10(array+1), label=c, linewidth=linewidth)

    ax[3].legend(loc="upper left")
    ax[3].set_title("Number of cases in log scale", fontsize=14, fontweight='bold')
    ax[3].set_xlabel(f"Days since February 22 2020")
    ax[3].grid()

    # Logarithm aligned
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        array = np.array(v)
        ax[4].plot(np.log10(array[align_indexes[c]:]+1), label=c, linewidth=linewidth)

    ax[4].legend(loc="upper left")
    ax[4].set_title("Number of cases in log scale", fontsize=14, fontweight='bold')
    ax[4].set_xlabel(f"Days since cases are around {align_around}")
    ax[4].grid()

    # Logarithm aligned Gradient
    for c, v in confirmed.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        array = np.array(v)
        alinged_array = array[align_indexes[c]:]
        log_array = np.log10(alinged_array+1)
        array = np.gradient(log_array)
        ax[5].plot(array, label=c, linewidth=linewidth)

    ax[5].legend(loc="upper left")
    ax[5].set_title("Gradient of number of cases in log scale", fontsize=14, fontweight='bold')
    ax[5].set_xlabel(f"Days since cases are around {align_around}")
    ax[5].grid()

    plt.savefig(path / 'countries_cases.png', dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_growth(growths, align_indexes, align_around, path):
    growth_rate, growth_rate_moving_average, growth_rate_global_moving_average = growths
    # Raw Growth Rate
    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(20, 10))
    ax = trim_axs(ax, 6)
    for c, v in growth_rate.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[0].plot(v, label=c, linewidth=linewidth)
        
    ax[0].legend(loc="upper left")
    ax[0].set_title("Growth Rate Raw", fontsize=14, fontweight='bold')
    ax[0].set_xlabel(f"Days since February 22 2020")
    ax[0].grid()

    # Raw Growth Rate
    for c, v in growth_rate_moving_average.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[1].plot(v, label=c, linewidth=linewidth)
        
    ax[1].legend(loc="upper left")
    ax[1].set_title("Growth Rate moving average 5 days", fontsize=14, fontweight='bold')
    ax[1].set_xlabel(f"Days since February 22 2020")
    ax[1].grid()

    for c, v in growth_rate_global_moving_average.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[2].plot(v, label=c, linewidth=linewidth)
        
    ax[2].legend(loc="upper left")
    ax[2].set_title("Growth Rate global moving average", fontsize=14, fontweight='bold')
    ax[2].set_xlabel(f"Days since February 22 2020")
    ax[2].grid()

    for c, v in growth_rate.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[3].plot(v[align_indexes[c]:], label=c, linewidth=linewidth)
        
    ax[3].legend(loc="upper left")
    ax[3].set_title("Growth Rate Raw", fontsize=14, fontweight='bold')
    ax[3].set_xlabel(f"Days since cases are around {align_around}")
    ax[3].grid()

    for c, v in growth_rate_moving_average.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[4].plot(v[align_indexes[c]:], label=c, linewidth=linewidth)
        
    ax[4].legend(loc="upper left")
    ax[4].set_title("Growth Rate moving average 5 days", fontsize=14, fontweight='bold')
    ax[4].set_xlabel(f"Days since cases are around {align_around}")
    ax[4].grid()

    for c, v in growth_rate_global_moving_average.items():
        if c == "Italy" or c == "VA":
            linewidth = 2.5
        else:
            linewidth = 1.4
        ax[5].plot(v[align_indexes[c]:], label=c, linewidth=linewidth)
        
    ax[5].legend(loc="upper left")
    ax[5].set_title("Growth Rate global moving average", fontsize=14, fontweight='bold')
    ax[5].set_xlabel(f"Days since cases are around {align_around}")
    ax[5].grid()

    plt.savefig(path / 'countries_gr.png', dpi=300, bbox_inches='tight')
    plt.close(fig)