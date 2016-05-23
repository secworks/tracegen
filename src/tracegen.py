#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=======================================================================
#
# tracegen.py
# -----------
# Tool for generating synthetic traces with side-channel leakage.
# This version is hard coded to simulate side-channel leakage
# in DES where XOR in the final round is the target. To this
# end we also generate the final ciphertext.
#
#
# Author: Joachim Strömbergson
# Copyright (c) 2016, Assured AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#=======================================================================

#-------------------------------------------------------------------
# Python module imports.
#-------------------------------------------------------------------
import sys
import os
import argparse
import datetime
import random
import matplotlib.pyplot as plt
import numpy
import ujson


#-------------------------------------------------------------------
# Defines.
#-------------------------------------------------------------------
# DIFF_POS is the position within the trace (from 0 to 100%)
# where the generated diff will be inserted.
DIFF_POS = 0.8

# If RAND_DIFF_POS is True, the sample position where diff will
# be inserted vill be normal randomized around the DIFF_POS with
# the extent of RAND_DIFF_WIDTH positions.
RAND_DIFF_POS = True
RAND_DIFF_WIDTH = 3


# If DISPLAY_AVERAGE, then the average trace of all generates
# traces will be calculated and plotted.
DISPLAY_AVERAGE = True


#-------------------------------------------------------------------
# decide_leakage_effect()
#
# Decide if we should a small difference to simulate leakage.
#-------------------------------------------------------------------
def decide_leakage_effect():
    return True


#-------------------------------------------------------------------
# get_index
#
# Get the index in which sample a side channel effect should
# be added. Currently triangle shape with fixed width."
#-------------------------------------------------------------------
def get_index(num_samples):
    return int((num_samples * DIFF_POS) + random.triangular(-RAND_DIFF_WIDTH, RAND_DIFF_WIDTH))


#-------------------------------------------------------------------
# get_base_samples()
#
# Generate a trace wit num_samples. The values in the samples
# simulates the average base noise level.
#-------------------------------------------------------------------
def get_base_samples(num_samples):
    return [0.0] * num_samples


#-------------------------------------------------------------------
# display_average_trace()
#
# Display the average trace calculated over all traces.
#-------------------------------------------------------------------
def display_average_trace(traces):
    num_samples = len(traces[0])

    average_trace = [0.0] * num_samples

    for t in xrange(len(traces)):
        for i in xrange(num_samples):
            average_trace[i] += traces[t][i]
    for i in xrange(num_samples):
        average_trace[i] = average_trace[i] / num_samples

    x_index = [i for i in xrange(num_samples)]
    plt.plot(x_index, average_trace)
    plt.show()


#-------------------------------------------------------------------
# gen_traces()
#
# Generate num_traces number of traces, each with num_samples.
# The traces ares stored in files in the destdir. There is also
# a DB crated that links the trace files to the generated
# ciphertexts.
#-------------------------------------------------------------------
def gen_traces(destdir, basenane, num_traces, num_samples, verbose=False):
    # Try to open the dest dir.

    # Generate or get basename.

    # Loop over all traces
    traces = []
    for t in xrange(num_traces):
        diff_sample = get_index(num_samples)
        if verbose:
            print("Sample where diff will be inserted: %d" % (diff_sample))
        samples = get_base_samples(num_samples)

        if decide_leakage_effect():
            samples[diff_sample] += 0.01
        traces.append(samples)

    if verbose:
        print("Generated traces:")
        print(traces)

    if DISPLAY_AVERAGE:
        display_average_trace(traces)


#-------------------------------------------------------------------
# main()
#
# Parse arguments and call the real dpa functionality.
#-------------------------------------------------------------------
def main():
    VERSION = '0.1 alpha'

    parser = argparse.ArgumentParser(version = VERSION,
                                     description = 'Generated traces with side-channel leakage\
                                      for testing side-channel analysis tools.')

    parser.add_argument("destdir", help = 'The destination file directory')

    parser.add_argument('-b', "--basename", action="store", default="currdate",
                        help = 'The base file name for target files. If omitted\
                        a simple name will be automatically generated.')

    parser.add_argument('-n' '--traces', action="store", dest="num_traces",
                            type=int, help="Number of traces to geneate. Default 1000", default=1000)

    parser.add_argument('-s' '--samples', action="store", dest="num_samples",
                            type=int, help="Number of samples in a trace. Default 1000", default=1000)

    parser.add_argument('-p', '--plot', action="store_true", dest='do_plot', default=False,
                            help="Plot the resulting average trace.")

    parser.add_argument('--verbose', action="store_true", default=False)

    args = parser.parse_args()

    gen_traces(args.destdir, args.basename, args.num_traces, args.num_samples, args.verbose)


#-------------------------------------------------------------------
# __name__
# Python thingy which allows the file to be run standalone as
# well as parsed from within a Python interpreter.
#-------------------------------------------------------------------
if __name__=="__main__":
    # Run the main function.
    sys.exit(main())

#=======================================================================
# EOF dpa.py
#=======================================================================
