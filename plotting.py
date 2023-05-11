# This file holds function used for ploting

import matplotlib.pyplot as plt
import numpy

def plot_trace(trace, name="plot.png"):
    """Plot single trace."""

    x = range(len(trace))
    y = trace

    plt.figure(figsize=(64, 36))
    plt.rcParams.update({'font.size': 64})
    plt.rcParams['agg.path.chunksize'] = 200
    plt.xlabel("Vzorky [n] →")
    plt.ylabel('Proudový odběr [-]  →')
    plt.axis([0, 1704402, -128, 128])
    plt.grid(True)
    plt.plot(x, y)
    plt.savefig(name)


def plot_traces(traces, highlight=None, name="plot.png", casual_traces_portion=0.25):
    """
    Plot multiple traces. Can highlight traces based on highlight indexies. 
    Highlight can be list or integer for single highlight trace.
    """

    #plt.figure(figsize=(34,20))
    #plt.rcParams.update({'font.size': 48})

    # Inicialize temp variable fot highlight traces
    x_template = range(traces[0].shape[0])
    highlighted_plots = []      # Records in format: {"x":[...], "y":[...]}

    # Handle highlight - separete highlighted traces and rest of traces
    if highlight:
        # Highlight parameter passed

        if type(highlight) == list:
            # Highlight parameter is type of list (multiple indexies)

            for i in highlight:
                # Highlight all traces specified by indexies

                highlighted_plots.append({"x":x_template, "y":traces[i]})
                numpy.delete(traces, (i), axis=0)

        elif  type(highlight) == numpy.uint8 or type(highlight) == int:
            # Highlight parameter is type of int (single index)

            highlighted_plots.append({"x":x_template, "y":traces[highlight]})
            numpy.delete(traces, (highlight), axis=0)
        
        else:
            # Not supported type of highlight parameter inserted

            raise TypeError(f"highlight parameter expected types are List and Int, got {type(highlight)} instead. \nHelp: Insert highlight parameter as list of traces indexis to be highlighted or single index of trace to be highlighted.")

    # Plot traces casual traces
    for i in range(int(len(traces)*casual_traces_portion) - 1):

        x = x_template
        y = traces[i]

        if highlight:
            # highlighting enable - casual traces will be blue
            plt.plot(x, y, color="blue")

        else:
            # highlighting disable - traces will be of different colors
            plt.plot(x, y)
        
    plt.plot(
        x_template, 
        traces[int(len(traces)*casual_traces_portion)],
        color="blue", 
        label="špatné odhady klíče"
    )

    # Plot highlighted traces
    if highlight:

        for plot in highlighted_plots:

            plt.plot(plot["x"], plot["y"], color="red", label="správný odhad klíče")

    
    plt.axis([0, 300000, -0.8, 0.8])
    plt.ylabel("Korelace [-] →")
    plt.xlabel("Vzorky [n] →")
    plt.legend()
    plt.grid(True)
    plt.savefig(name)