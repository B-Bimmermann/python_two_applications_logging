#!/usr/bin/python3
# Plot the qemu logs from the

###############################
import argparse
import sys
import pathlib
import plotly

# Create random data with numpy
import numpy as np
###############################




###############################
# Parse the Options
def plot_qemu_log(arglist):
    # Set the argument Parser
    parser = argparse.ArgumentParser(description='Plot the qemu applications')
    parser.add_argument('logfile_path', help='Path for the logfile')
    parser.add_argument('-v', "--verbose", dest='verbose', action='store_true',
                        help='Print verbose information (default: false)')

    # Parse the arguments from arglist
    args = parser.parse_args(arglist)

    # check the scripts exists
    logfile_path = pathlib.Path(args.logfile_path).resolve()

    # If the path does not exist we must stop
    if not logfile_path.exists():
        raise ValueError(
            'Logfile path does not exit. Please check the path'
            + 'Path was: ' + args.logfile_path)
    # else make it to a string
    else:
        logfile_path = str(logfile_path)

    n = 500
    random_x = np.linspace(0, 1, n)
    random_y = np.random.randn(n)

    # Create a trace
    trace = plotly.graph_objs.Scatter(
        x=random_x,
        y=random_y
    )

    data = [trace]

    plotly.plotly.plot(data, filename='basic-line')


    # end
    print('finsed')


# END OF DEF LOG_MANI(arglist) ####
#############################


#############################
# main
if __name__ == "__main__":
    plot_qemu_log(sys.argv[1:])
# END OF DEF __main__ ####
#############################

