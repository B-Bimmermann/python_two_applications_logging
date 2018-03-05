#!/usr/bin/python3
# Measure and log the time for two applications


###############################
import argparse
import logging
import sys
import subprocess
import threading
import multiprocessing
import time
import datetime
import pathlib


###############################

###############################
# Thread function for the stdout logging
def stdout_log(logger, proc, log_name):
    while proc.poll() is None:
        line = proc.stdout.readline().decode("utf-8")
        # The logger add a newline after every message.
        # That's why we strip the last \n
        logger.name = log_name
        if line and line != ' ':
            if "END END MY END" in line:
                print("Have close proc ...")
                proc.terminate()
            else:
                logger.info(line.rstrip("\n"))


###############################

###############################
# Thread function for the stderr logging
def stderr_log(logger, proc, log_name):
    while proc.poll() is None:
        line = proc.stderr.readline().decode("utf-8")
        # The logger add a newline after every message.
        # That's why we strip the last \n
        logger.name = log_name
        if line and line != ' ':
            if "END END MY END" in line:
                proc.terminate()
            else:
                logger.error(line.rstrip("\n"))


###############################


###############################
# open the subprocess and connect threads for the log to it
def create_subprocess_with_loggger(logger, processname, processname_short, process_argument):
    # open a subprocess and pipe the std output to threads
    if process_argument:
        proc = subprocess.Popen([processname, process_argument], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen([processname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Start the logging threads
    thread_stdout_log = threading.Thread(target=stdout_log, args=(logger, proc, processname_short))
    thread_stderr_log = threading.Thread(target=stderr_log, args=(logger, proc, processname_short))

    # Start the logging threads
    thread_stdout_log.start()
    thread_stderr_log.start()

    # Wait until the thread terminates
    while thread_stdout_log.is_alive() and thread_stderr_log.is_alive():
        pass

    # Kill the subprocess
    proc.terminate()


###############################

###############################
# Parse the Options
def log_apli(arglist):
    # Set the argument Parser
    parser = argparse.ArgumentParser(description='Messure and log the time for two applications')
    parser.add_argument('application_1_path', help='Path to first application')
    parser.add_argument('application_2_path', help='Path to second application')
    parser.add_argument('logfile_path', help='Path for the logfile')
    parser.add_argument('-a1', '--arguments_application_1', dest='arguments_application_1',
                        help='Optinal arguments for the first application')
    parser.add_argument('-a2', '--arguments_application_2', dest='arguments_application_2',
                        help='Optinal arguments for the second application')
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
    application_1_path = pathlib.Path(args.application_1_path).resolve()
    application_2_path = pathlib.Path(args.application_2_path).resolve()

    # If the path does not exist we must stop
    if not (application_1_path.exists() and application_2_path.exists()):
        if not application_1_path.exists():
            raise ValueError(
                'Application path for the first application does not exit. Please check the application path'
                + 'Path was: ' + args.application_1_path)
        else:
            raise ValueError(
                'Application path for the second application does not exit. Please check the application path.'
                + 'Path was: ' + args.application_2_path)
    # else make it to a string
    else:
        application_1_path = str(application_1_path)
        application_2_path = str(application_2_path)

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
    ch = logging.StreamHandler()

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

    # # format the date (with millisekonds)
    # formatter = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S.%s")

    # format the date (without millisekonds)
    formatter = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S")

    # set the formater
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # set the loglevel
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create the names for the applications
    application_1_name = application_1_path.rsplit('/', 1)[1]
    application_2_name = application_2_path.rsplit('/', 1)[1]

    # Print the path
    logger.debug("Path to the first application " + application_1_path)
    logger.debug("Path to the second application " + application_2_path)
    logger.debug("Path to the logfile " + logfile_path_with_date)

    logger.debug("Short name for the first application " + application_1_name)
    logger.debug("Short name for second application " + application_2_name)

    # Start
    logger.info('Start')

    # create processes for the subprocess
    process_one = multiprocessing.Process(target=create_subprocess_with_loggger,
                                          args=(
                                              logger,
                                              application_1_path,
                                              application_1_name,
                                              args.arguments_application_1))
    process_two = multiprocessing.Process(target=create_subprocess_with_loggger,
                                          args=(
                                              logger,
                                              application_2_path,
                                              application_2_name,
                                              args.arguments_application_2))

    # start the first process
    process_one.start()
    # wait and then start the second process
    time.sleep(1.5)
    process_two.start()

    # wait for finishing
    while process_one.is_alive() and process_two.is_alive():
        pass

    # close all processes
    if process_one.is_alive():
        process_one.terminate()
    if process_two.is_alive():
        process_two.terminate()
    logger.info('finsed')


# END OF DEF LOG_MANI(arglist) ####
#############################


#############################
# main
if __name__ == "__main__":
    log_apli(sys.argv[1:])
# END OF DEF __main__ ####
#############################
