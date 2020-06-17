#! /usr/bin/python


#### Imports

# External Libraries
import argparse
import logging
import os
import sys
import time
import wave

#### Logger
log = logging.getLogger('root')
log_format = "[%(asctime)s] %(message)s"
logging.basicConfig(format = log_format)
log.setLevel(logging.DEBUG)


def main():
    ### Parse and display arguments
    arguments = parse_arguments()

    ### Get Read File Handle
    rfh = wave.open(arguments.source, mode="rb")

    ### Get Slice Information
    [ frames_per_slice, remainder ] = get_frames_per_slice(arguments, rfh)

    ### Write Slices
    write_slices(arguments, rfh, frames_per_slice, remainder)


def parse_arguments():

    ### Get arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument( "-s", "--source",  help = "Source Sound File",  required=True )
    parser.add_argument( "-d", "--destination_directory", help = "Split Files Destination", required=True)
    parser.add_argument( "-p", "--prefix",  help = "Sliced File Prefix",  required=False )
    parser.add_argument( "-n", "--number_of_slices", help = "Number of Slices", required=True)
    arguments = parser.parse_args()

    ### Print Arguments
    log.info( "Source                 - %s" % arguments.source)
    log.info( "Destination Directory  - %s" % arguments.destination_directory)
    log.info( "Number of Slices       - %s" % arguments.number_of_slices)

    ### Print Optional Arguments
    if (arguments.prefix is not None):
        log.info( "Prefix                 - %s" % arguments.prefix)

    return arguments

def get_frames_per_slice(arguments, rfh):

    ### Get Number of Frames for the File
    frames = rfh.getnframes()

    ### Get Number of Frames Per Slice
    frames_per_slice = frames // int(arguments.number_of_slices)

    ### Get Leftover Frames
    remainder = frames % int(arguments.number_of_slices)

    log.info("Number of Frames       - %s" % frames)
    log.info("Frames Per Slice       - %s" % frames_per_slice)
    log.info("Leftover Frames        - %s" % remainder)

    return [ frames_per_slice, remainder ]

def write_slices(arguments, rfh, frames_per_slice, remainder):

    # Get Filename Prefix
    if (arguments.prefix is not None):
        prefix = arguments.prefix
    else:
        prefix = arguments.source

    # Get File Details
    nchannels = rfh.getnchannels()
    sampwidth = rfh.getsampwidth()
    framerate = rfh.getframerate()

    current_pos = 0

    # Write Files
    for wave_slice in range(int(arguments.number_of_slices)):
        file_name = arguments.destination_directory + "/" + prefix + "_" + str(wave_slice + 1).rjust(3, '0') + ".wav"
        log.info("Writing                - %s" % file_name)

        # Set Position of Read Handle
        log.info("Set Position           - %s" % current_pos)
        rfh.setpos(current_pos)

        # Read And Increment Position
        if (wave_slice < (int(arguments.number_of_slices) - remainder)):
            data = rfh.readframes(frames_per_slice)
            current_pos = current_pos + frames_per_slice
        else:
            data = rfh.readframes(frames_per_slice + 1)
            current_pos = current_pos + frames_per_slice + 1

        # Write File
        if (not os.path.isdir(arguments.destination_directory)):
            os.mkdir(arguments.destination_directory)

        wfh = wave.open(file_name, mode="wb")
        wfh.setnchannels(nchannels)
        wfh.setsampwidth(sampwidth)
        wfh.setframerate(framerate)
        wfh.writeframes(data)
        wfh.close()

if __name__ == "__main__":
    main()
