import matplotlib.pyplot as plt
import numpy as np


def db_to_linear(db: float):
    return 10 ** (db / 20)


def normalize_filter(filter_params):
    filter_norm = filter_params.copy()
    filter_norm["f_pass"] = (filter_norm["f_pass"] / (0.5 * filter_norm["fs"])) * np.pi
    filter_norm["tr_band"] = (
        filter_norm["tr_band"] / (0.5 * filter_norm["fs"])
    ) * np.pi
    filter_norm["fs"] = np.pi

    return filter_norm


def cost_LP_filter(
    f_response: np.ndarray,
    d1: float,
    d2: float,
    f_pass: float,
    transition_band: float = 0,
):

    N_fft = f_response.shape[0]
    n_passband = int(np.ceil((f_pass * N_fft) / np.pi))
    n_transition = int(np.ceil(((f_pass + transition_band) * N_fft) / np.pi))

    cost = 0.0
    # Passband section (in linear best = 1)
    d_sqr = (f_response[: n_passband - 1] - 1) ** 2
    cost += np.sum(np.where(d_sqr > d1**2, np.sqrt(d_sqr), 0))

    # Stopband section (in linear best = 0)
    const_penalty = 10
    d = f_response[n_transition:] - d2
    cost += np.sum(np.where(d > 0.0, const_penalty * d, 0))

    return cost


def display_LP_filter(f, f_response, filter_params):
    """_summary_

    Args:
        f (_type_): _description_
        f_response (_type_): _description_
        filter_params (_type_): _description_
    """

    d1 = filter_params["d1_db"]
    d2 = filter_params["d2_db"]
    f_pass = filter_params["f_pass"]
    tr_band = filter_params["tr_band"]
    m_order = filter_params["m_order"]

    # Draw limits
    plt.hlines(-d1, 0, f_pass, linestyles="dashed", colors="g")
    plt.hlines(
        +d1, 0, f_pass, linestyles="dashed", colors="g", label="Expected: A_pass"
    )
    plt.hlines(
        d2,
        f_pass + tr_band,
        np.pi,
        linestyles="dashed",
        colors="r",
        label="Expected: A_stop",
    )

    # Draw filter response
    labels = ["Original  filter", "Modified filter"]
    for i in range(f.shape[0]):
        plt.plot(f[i], 20 * np.log10(abs(f_response[i])), label=labels[i])

    plt.xlim([0, np.pi])
    plt.ylim([-100, 5])
    plt.legend()
    plt.title("FIR filter, M={}".format(m_order))
    plt.show()
