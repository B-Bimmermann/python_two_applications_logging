#!/usr/bin/python3
# Messure and log the time for two aplications


###############################
import argparse
import logging
import sys
import subprocess
import threading
import multiprocessing
import time
import os
###############################

###############################
# Thread funktion for the stdout logging
def stdout_log(logger,proc,log_name):
    while proc.poll() is None:
        line = proc.stdout.readline().decode("utf-8")
        # The logger add a newline afther every message.
        # That's why we strip the last \n
        logger.name = log_name
        if line:
            logger.info(line.rstrip("\n"))
###############################

###############################
# Thread funktion for the stderr logging
def stderr_log(logger,proc,log_name):
    while proc.poll() is None:
        line = proc.stderr.readline().decode("utf-8")
        # The logger add a newline afther every message.
        # That's why we strip the last \n
        logger.name = log_name
        if line:
            logger.error(line.rstrip("\n"))
###############################


###############################
# open the subprocess and connect threads for the log to it
def create_subprocess_with_loggger(logger,processname,processname_short,process_argument):
    # open a subprocess and pipe the std output to threads
    if process_argument:
        proc = subprocess.Popen([processname, process_argument], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen([processname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Start the logging threads
    thread_stdout_log = threading.Thread(target=stdout_log, args=(logger,proc,processname_short))
    thread_stderr_log = threading.Thread(target=stderr_log, args=(logger,proc,processname_short))

    # Start the logging threads
    thread_stdout_log.start()
    thread_stderr_log.start()

    # Wait until the thread terminates
    thread_stdout_log.join()
    thread_stderr_log.join()
###############################

###############################
# Parse the Options
def log_mani(arglist):

    # Set the argument Parser
    parser = argparse.ArgumentParser(description='Messure and log the time for two aplications')
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
    parser.add_argument('-v',"--verbose", dest='verbose', action='store_true',
                        help='Print verbose information (default: false)')
    parser.add_argument('-s', '--shared_folder_path', dest='shared_folder_path',
                        help='Path to the shared folder to clean it up')

    # Parse the arguments from arglist
    args = parser.parse_args(arglist)

    # create logger
    logger = logging.getLogger()

    # create file handler which logs even debug messages
    fh = logging.FileHandler(args.logfile_path)

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

    # format the date (with millisekonds)
    formatter = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S.%s")
    fh.setFormatter(formatter)
    # format the date (without millisekonds)
    formatter_console = logging.Formatter(format_string, datefmt="%d-%m-%Y %H:%M:%S")
    ch.setFormatter(formatter_console)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # set the loglevel
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create the names for the applications
    application_1_name = (os.path.split(args.application_1_path))[1]
    application_2_name = (os.path.split(args.application_2_path))[1]

    # Print the path
    logger.debug("Path to the first application " +  args.application_1_path)
    logger.debug("Path to the second application " + args.application_2_path)
    logger.debug("Path to the logfile " + args.logfile_path)

    logger.debug("Short name for the first application " +  application_1_name)
    logger.debug("Short name for second application "    +  application_2_name)

    if args.shared_folder_path:
        logger.debug("Path to the shared folder  " + args.shared_folder_path)

    # Start
    logger.info('Start')

    # create processes for the subprocess
    process_one = multiprocessing.Process(target=create_subprocess_with_loggger,
                                          args=(
                                          logger,
                                          args.application_1_path,
                                          application_1_name,
                                          args.arguments_application_1))
    process_two = multiprocessing.Process(target=create_subprocess_with_loggger,
                                          args=(
                                          logger,
                                          args.application_2_path,
                                          application_2_name,
                                          args.arguments_application_2))

    #start the first process
    process_one.start()
    # wait and then start the second process
    time.sleep(1.5)
    process_two.start()


    # wait for finishing
    process_one.join()
    process_two.join()

    logger.info('finsed')
### END OF DEF LOG_MANI() ####


#############################
# main
if __name__ == "__main__":
    log_mani(sys.argv[1:])
### END OF DEF __main__ ####
