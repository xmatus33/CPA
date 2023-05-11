# This file contains Correlation Power Analysis (CPA) attack implementation
# on AES-128. Traces used are from DPAv4.2 Contest (https://www.dpacontest.org/v4/42_traces.php)
# Traces from DPAv4.2 are divided into 16x2 subsets of 2,500 traces each.
# Index file is also present, holding metadata for all dataset.

import math
import numpy as np

from tables import S_box, HW
from dpa_parser import load_traces, parse_index_file


def calculate_rank(max_peaks_array, correct_key):
    """Calculate partial guessing entropy."""

    peak_for_correct_key = max_peaks_array[correct_key]

    # Sort in descending order
    g = np.sort(max_peaks_array)[::-1]

    return np.where(g == peak_for_correct_key)[0][0]


def cpa(
    traces,
    plaintexts,
    offsets,
    keys,
    GROUP_SIZE=300,
    search_window_start=0,
    search_window_end=None,
    attack_on_bytes=range(16)
):
    """CPA attack."""

    # Set defalt search_window_end to the last sample (index) of traces
    if not search_window_end:
        search_window_end = len(traces[0]) - 1

    # Limit attack on search window
    traces = traces[:, search_window_start:search_window_end]

    TRACES_NUM = len(traces)
    TRACES_LEN = len(traces[0])

    MASK = [
        0x03,
        0x0C,
        0x35,
        0x3A,
        0x50,
        0x5F,
        0x66,
        0x69,
        0x96,
        0x99,
        0xA0,
        0xAF,
        0xC5,
        0xCA,
        0xF3,
        0xFC,
    ]

    guessed_key = []
    ranks = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    cpa_outputs = []
    max_peaks = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    for byte_index in attack_on_bytes:
        print(f"Calculation correlation matrix for {byte_index + 1}. key byte")

        numerator = np.zeros(shape=(256, TRACES_LEN))
        h_diff_sum = np.zeros(256)
        t_diff_sum = np.zeros(TRACES_LEN)

        num_iterations = math.ceil(TRACES_NUM / GROUP_SIZE)

        for i_group in range(num_iterations):
            # Calculate one group

            start = i_group * GROUP_SIZE
            end = start + GROUP_SIZE
            if end > TRACES_NUM:
                end = TRACES_NUM

            print(f"start: {start}, end: {end}")

            # Intermediate values
            offsets_in = np.array(
                [i[byte_index] for i in offsets[start:end]]
            )
            PT = np.array(
                [i[byte_index] for i in plaintexts[start:end]]
            )
            mask2 = np.array(
                [MASK[(offs + 1) % 16] for offs in offsets_in]
            )
            key_guess = np.array([i for i in range(256)])
            K_PT_matrix = np.bitwise_xor(
                key_guess[:, np.newaxis], PT[np.newaxis, :]
            )

            attack_input = np.bitwise_xor(
                S_box(K_PT_matrix), mask2
            )
            power_model = HW(attack_input).astype("uint8")

            mean_h = np.mean(power_model, axis=1)           # x_bar
            mean_t = np.mean(traces[start:end], axis=0)     # y_bar

            # x - x_bar
            h_diff = power_model - mean_h[:, np.newaxis]
            # y - y_bar
            t_diff = traces[start:end] - mean_t
            # sum((x - x_bar)(y - y_bar))
            numerator += np.matmul(h_diff, t_diff)
            # (x - x_bar)^2
            h_diff = h_diff**2
            # (y - y_bar)^2
            t_diff = t_diff**2
            # sum((x - x_bar)^2)
            h_diff_sum += np.sum(h_diff, axis=1)
            # sum((y - y_bar)^2)
            t_diff_sum += np.sum(t_diff, axis=0)
            # sum((x - x_bar)^2) * sum((y - y_bar)^2)
            denominator = (
                h_diff_sum[:, np.newaxis] * t_diff_sum[np.newaxis, :]
            )

            denominator = np.sqrt(denominator)
            cpa_output = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator!=0)
            max_cpa = np.max(np.absolute(cpa_output), axis=1)
            key_byte = np.argmax(max_cpa)
            
            # Values for ploting max peaks evolution
            argmax_cpa = np.argmax(np.absolute(cpa_output), axis=1)
            max_values = cpa_output[range(len(argmax_cpa)),argmax_cpa]  # Not in absolute value compare to max_cpa
            max_peaks[byte_index].append(max_values)

            # Values for ploting ranks
            ranks[byte_index].append(calculate_rank(max_cpa, keys[0][byte_index]))
        
        cpa_outputs.append(cpa_output)

        print(f"Guessed {byte_index + 1}. key byte:", key_byte)
        print(f"Correct {byte_index + 1}. key byte:", keys[0][byte_index])

        guessed_key.append(key_byte)

        print(f"Guessed key: ", np.array(guessed_key))
        print(f"Correct key: ", keys[0])

    return guessed_key, ranks, cpa_outputs, max_peaks


if __name__ == "__main__":

    TRACES_NUM = 300
    GROUP_SIZE = 100

    # Load traces
    # traces = load_traces("./DPAv4_2/k00/", num_traces=TRACES_NUM)
    traces = np.load("example_traces_300.npy")

    # Load metadata
    # meta_d = parse_index_file("/4TB/database/DPAv4_2/dpav4_2_index", TRACES_NUM)
    meta_d = parse_index_file("index_file_striped.txt", TRACES_NUM)

    guessed_key, ranks, cpa_outputs, max_peaks = cpa(
        traces,
        meta_d["plaintexts"][:],
        meta_d["offsets"][:],
        meta_d["keys"][:],
        GROUP_SIZE=GROUP_SIZE,
        attack_on_bytes=range(0,16)
    )
