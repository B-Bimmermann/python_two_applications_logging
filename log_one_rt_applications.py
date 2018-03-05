#!/usr/bin/python3
# Measure and log the time for one rt applications


###############################
import argparse
import logging
import sys
import subprocess
import threading
import datetime
import pathlib


###############################

###############################
# Thread function for the stdout logging
def stdout_log(logger, proc):
    while proc.poll() is None:
        line = proc.stdout.readline().decode("utf-8")
        # The logger add a newline after every message.
        # That's why we strip the last \n
        if line and line != ' ':
            if "END END MY END" in line:
                print("Have close proc ...")
                proc.terminate()
            else:
                logger.info(line.rstrip("\n"))


###############################

###############################
# Thread function for the stderr logging
def stderr_log(logger, proc):
    while proc.poll() is None:
        line = proc.stderr.readline().decode("utf-8")
        # The logger add a newline after every message.
        # That's why we strip the last \n
        if line and line != ' ':
            if "END END MY END" in line:
                proc.terminate()
            else:
                logger.error(line.rstrip("\n"))


###############################

###############################
# Parse the Options
def log_apli(arglist):
    # Set the argument Parser
    parser = argparse.ArgumentParser(description='Messure and log the time for one rt applications',
                                     epilog='Example of use: '
                                            './log_one_rt_applications.py '
                                            '-v /usr/bin/mpirun $LOG_PATH/LOG.txt '
                                            '-a "-np 7 $MANIFOLD_PATH/manifold/simulator/smp/QsimProxy/smp_llp '
                                            '$MANIFOLD_PATH/manifold/simulator/smp/config/confZCU102.cfg '
                                            '$MANIFOLD_PATH/manifold/simulator/smp/benchmark/graphBig_a64/bc.tar"')

    parser.add_argument('application_path', help='Path to first application')
    parser.add_argument('logfile_path', help='Path for the logfile')
    parser.add_argument('-a', '--arguments_application', dest='arguments_application',
                        help='Optinal arguments for the first application')
    parser.add_argument('-nc', '--no_console_output', dest='log_console', action='store_false',
                        help='Don\'t log to the console. (default: Log to console and file)')
    parser.add_argument('-nt', '--no_time', dest='show_time', action='store_false',
                        help='Don\'t print the time for each line. (default: true)')
    parser.add_argument('-nT', '--no_sys_time', dest='show_systime', action='store_false',
                        help='Don\'t print the system time for each line. (default: true)')
    parser.add_argument('-v', "--verbose", dest='verbose', action='store_true',
                        help='Print verbose information (default: false)')

    # Parse the arguments from arglist
    args = parser.parse_args(arglist)

    # create logger
    logger = logging.getLogger()

    # check the scripts exists
    application_path = pathlib.Path(args.application_path).resolve()

    # If the path does not exist we must stop
    if not application_path.exists():
        raise ValueError(
            'Application path for the first application does not exit. Please check the application path'
            + 'Path was: ' + args.application_path)
    # else make it to a string
    else:
        application_path = str(application_path)

    # set current date to the logfile
    if args.logfile_path[:-4] == ".txt":
        logfile_path_with_date = args.logfile_path[:-4] + datetime.datetime.now().strftime(
            "%d-%m-%Y--%H:%M:%S") + ".txt"
    else:
        logfile_path_with_date = args.logfile_path + "--" + datetime.datetime.now().strftime(
            "%d-%m-%Y--%H:%M:%S") + ".txt"

    # create file handler which logs even debug messages
    fh = logging.FileHandler(logfile_path_with_date)

    # create console handler
    if args.log_console:
        ch = logging.StreamHandler()
    else:
        ch = False

    # create formatter and add it to the handlers
    #     %(asctime)s         Textual time when the LogRecord was created
    #     %(msecs)d           Millisecond portion of the creation time
    #     %(relativeCreated)d Time in milliseconds when the LogRecord was created,
    #                         relative to the time the logging module was loaded
    #                         (typically at application startup time)
    format_string = "%(name)-6s ||| %(levelname)-6s ||| %(message)s "
    if args.show_time:
        format_string = 'time: %(relativeCreated)-20d (ms)||| ' + format_string
    if args.show_systime:
        format_string = 'systime: %(asctime)-15s ||| ' + format_string

    # # format the date (with milliseconds)
    # formatter = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S.%s")

    # format the date (without milliseconds)
    formatter = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S")

    # set the formater
    fh.setFormatter(formatter)

    if args.log_console:
        ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    if args.log_console:
        logger.addHandler(ch)

    # set the loglevel
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create the names for the applications
    application_name = application_path.rsplit('/', 1)[1]
    logger.name = application_name

    # Print the path
    logger.debug("Path to the first application " + application_path)
    logger.debug("Path to the logfile " + logfile_path_with_date)
    logger.debug("Short name for the first application " + application_name)
    if args.arguments_application:
        logger.debug("application arguments: " + args.arguments_application)

    # Start
    logger.info('Start')

    # open a subprocess one
    if args.arguments_application:
        # Create the subprocess command
        command = [application_path] + args.arguments_application.split()
        # Open the subprocess
        proc_application = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        # Open the subprocess
        proc_application = subprocess.Popen([application_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Start the logging threads
    thread_stdout_app1_log = threading.Thread(target=stdout_log, args=(logger, proc_application))
    thread_stderr_app1_log = threading.Thread(target=stderr_log, args=(logger, proc_application))

    # Start the logging threads
    thread_stdout_app1_log.start()
    thread_stderr_app1_log.start()

    # Wait until the thread terminates
    while thread_stdout_app1_log.is_alive() and thread_stderr_app1_log.is_alive():
        pass

    logger.info('finsed')


# END OF DEF LOG_MANI(arglist) ####
#############################


#############################
# main
if __name__ == "__main__":
    log_apli(sys.argv[1:])
# END OF DEF __main__ ####
#############################
