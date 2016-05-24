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
import cPickle as pickle
import ujson


#-------------------------------------------------------------------
# Defines.
#
# A lot of these could (should) be turned into flags w defaults.
# They control a lot of the behaviour.
#-------------------------------------------------------------------
# DIFF_POS is the position within the trace (from 0 to 100%)
# where the generated diff will be inserted.
DIFF_POS = 0.8

# If RAND_DIFF_POS is True, the sample position where diff will
# be inserted vill be normal randomized around the DIFF_POS with
# the extent of RAND_DIFF_WIDTH positions.
RAND_DIFF_POS = True
RAND_DIFF_WIDTH = 3

# If DISPLAY_EXAMPLE, then the first trace generated is displayed
# as an example.
DISPLAY_EXAMPLE = True

# If DISPLAY_AVERAGE, then the average trace of all generates
# traces will be calculated and plotted.
DISPLAY_AVERAGE = True

# If ALWAYS_LEAK_OP then the leakage decision function will always
# return True and the leakage will always be added.
ALWAYS_LEAK_OP = False

# LEAKAGE_BIT is the bit in the round function we look at for
# doing leakage decision.
LEAKAGE_BIT = 0

# ROUND_KEY is the 6 bit value used as round key. Note that this
# means that the round key is repeated instances of ROUND_KEY
ROUND_KEY = 42


#-------------------------------------------------------------------
# flatten()
#
# Flatten (merge) a list of list into a single list. Python does
# not have a good operator for this.
#-------------------------------------------------------------------
def flatten(bitlist):
    res = []
    for i in bitlist:
        res += i
    return res


#-------------------------------------------------------------------
# bl2i()
#
# Convert a given list of bits to an integer.
#-------------------------------------------------------------------
def bl2i(bitlist):
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out


#-------------------------------------------------------------------
# i2b()
#
# Convert an integer to an array of bits with a given width.
#-------------------------------------------------------------------
def i2b(width, i):
    return [1 if b=='1' else 0 for b in '{0:0(width)b}'.format(i)]


#-------------------------------------------------------------------
# des_s()
#
# Convert a given list with six bits to the output of the
# given DES S-box.
#-------------------------------------------------------------------
def des_s(sbox, blist):
    s = [[14,  4, 13, 01,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7,
           0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8,
           4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0,
          15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13],

         [15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10,
           3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5,
           0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15,
          13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9],

         [10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8,
          13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1,
          13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7,
           1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12],

         [ 7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15,
          13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9,
          10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4,
           3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14],

         [ 2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9,
          14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6,
           4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14,
          11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3],

         [12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11,
          10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8,
           9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6,
           4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13],

         [ 4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1,
          13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6,
           1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2,
           6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12],

         [13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7,
           1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2,
           7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8,
           2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11]]


    column = bl2i([blist[0], blist[5]]) * 16
    row = bl2i(blist[1:5])
    s_res = s[sbox][(row + column)]
    return s_res


#-------------------------------------------------------------------
# final_des_round()
#
# This function will generate a 64 bit random fake result from the
# next to final round and then given the rkey value perform
# final round operation including final permutation. The function
# returns the generated ciphertext and if the LEAKAGE_BIT
# in the specific calculation would cause a change 0->1 and
# therefore a leakage.
#-------------------------------------------------------------------
def final_des_round(rbit, rkey, verbose = False):
    e = [31,  0,  1,  2,  3,  4,  3,  4,  5,  6,  7,  8,
          7,  8,  9, 10, 11, 12, 11, 12, 13, 14, 15, 16,
         15, 16, 17, 18, 19, 20, 19, 20, 21, 22, 23, 24,
         23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31,  0]

    p = [15,  6, 19, 20, 28, 11, 27, 16, 00, 14, 22, 25,
          4, 17, 30,  9,  1,  7, 23, 13, 31, 26,  2,  8,
         18, 12, 29,  5, 21, 10,  3, 24]

    ip = [57, 49, 41, 33, 25, 17,  9,  1, 59, 51, 43, 35, 27, 19, 11,  3,
          61, 53, 45, 37, 29, 21, 13,  5, 63, 55, 47, 39, 31, 23, 15,  7,
          56, 48, 40, 32, 24, 16,  8,  0, 58, 50, 42, 34, 26, 18, 10,  2,
          60, 52, 44, 36, 28, 20, 12,  4, 62, 54, 46, 38, 30, 22, 14,  6]

    # Generate a random round result for round 15.
    l15 = [random.randint(0, 1) for i in range(32)]
    r15 = [random.randint(0, 1) for i in range(32)]

    # Expand r15, expand rkey and calculate f using s-boxes and p.
    exp_r = [int(r15[e[i]]) for i in xrange(48)]
    exp_rkey = [1 if b=='1' else 0 for b in '{0:06b}'.format(rkey)] * 8
    rxrkey = [(a ^ b) for a, b in zip(exp_r, exp_rkey)]
    s_split = [rxrkey[(i * 6) : ((i + 1) * 6)] for i in xrange(8)]
    s_res = [des_s(i, s_split[i]) for i in xrange(8)]
    s_bits = flatten([[1 if b=='1' else 0 for b in '{0:04b}'.format(i)] for i in s_res])
    f_res = [s_bits[p[i]] for i in xrange(32)]

    # Perform xor-operation using calculated f_res on left part of round 15 result.
    # Note that we also do final flip of L<->R using name notation.
    # Also create l16 which is a copy of r15
    r16 = [(a ^ b) for a, b in zip(l15, f_res)]
    l16 = r15[:]

    # We flip the order according to spec to create preoutput and gen ciphertext.
    preoutput = r16 + l16
    ciphertext = [preoutput[ip[i]] for i in xrange(64)]

    # Determine if the final round caused a leakage or not.
    # That is we have a zero being changed to a one.
    leakage = ((l15[rbit] == 0) and (r16[rbit] == 1))

    return (leakage, ciphertext)


#-------------------------------------------------------------------
# decide_leakage_effect()
#
# Decide if we should a small difference to simulate leakage.
#-------------------------------------------------------------------
def decide_leakage_effect():
    if ALWAYS_LEAK_OP:
        return (True, [0] * 64)
    return final_des_round(LEAKAGE_BIT, ROUND_KEY)


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
def get_base_samples(num_samples, noise_level):
    baseline_trace = []
    for i in xrange(num_samples):
        baseline_trace.append(random.uniform(-noise_level, noise_level))
    return baseline_trace


#-------------------------------------------------------------------
# display_trace()
#
# Display the given trace.
#-------------------------------------------------------------------
def display_trace(trace):
    x_index = [i for i in xrange(len(trace))]
    plt.plot(x_index, trace)
    plt.show()


#-------------------------------------------------------------------
# display_average_trace()
#
# Display the average trace calculated over all traces.
#-------------------------------------------------------------------
def display_average_trace(traces):
    (trace, ciphertext) = traces[0]

    num_samples = len(trace)
    average_trace = [0.0] * num_samples

    for t in xrange(len(traces)):
        (trace, ciphertext) = traces[t]
        for i in xrange(num_samples):
            average_trace[i] += trace[i]
    for i in xrange(num_samples):
        average_trace[i] = average_trace[i] / num_samples

    display_trace(average_trace)


#-------------------------------------------------------------------
# dump_traces()
#-------------------------------------------------------------------
def dump_traces(dest_dir, base_name, traces, verbose=False):
    if dest_dir[-1] != "/":
        dest_dir += "/"

    dst_file_ctr = 0
    cipher_db = []
    for (trace, ciphertext) in traces:
        dst_file_name = dest_dir + base_name + "_" + str(dst_file_ctr).zfill(8) + ".dpa"
        if verbose:
            print("Writing converted data to file: %s" % dst_file_name)

        with open(dst_file_name, 'wb') as curr_dst_file:
            ujson.dump(trace, curr_dst_file)
        dst_file_ctr += 1
        cipher_db.append((dst_file_name, ciphertext))

    # Save the DB with ciphertexts and file names.
    dst_cipher_file_name = dest_dir + base_name + "_ciphertexts.dpb"
    with open(dst_cipher_file_name, 'wb') as curr_dst_file:
        pickle.dump(cipher_db, curr_dst_file, pickle.HIGHEST_PROTOCOL)


#-------------------------------------------------------------------
# gen_traces()
#
# Generate num_traces number of traces, each with num_samples.
# The traces ares stored in files in the destdir. There is also
# a DB crated that links the trace files to the generated
# ciphertexts.
#-------------------------------------------------------------------
def gen_traces(destdir, basename, num_traces, num_samples,
                   noise_level, leakage_level, verbose=False):

    num_leaks = 0
    traces = []
    for t in xrange(num_traces):
        if t % 1000 == 0:
            print("trace: %08d" % t)
        diff_sample = get_index(num_samples)
        if verbose:
            print("Sample where diff will be inserted: %d" % (diff_sample))
        trace = get_base_samples(num_samples, noise_level)

        (leakage, ciphertext) = decide_leakage_effect()

        if leakage:
            trace[diff_sample] += leakage_level
            num_leaks += 1
        traces.append((trace, ciphertext))

    print("Number of traces with leakage: %08d" % num_leaks)

    if verbose:
        print("Generated traces:")
        print(traces)

    if DISPLAY_EXAMPLE:
        (trace, ciphertext) = traces[0]
        display_trace(trace)

    if DISPLAY_AVERAGE:
        display_average_trace(traces)

    dump_traces(destdir, basename, traces, verbose)


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

    parser.add_argument('-r' '--random-noise', action="store", dest="noise_level",
                            type=float, help="The peak +/- random noise level in traces. Default 0.05",
                            default=0.05)

    parser.add_argument('-l' '--leakage-level', action="store", dest="leakage_level",
                            type=float, help="The positive leakage level in traces. Default 0.01",
                            default=0.01)

    parser.add_argument('-p', '--plot', action="store_true", dest='do_plot', default=False,
                            help="Plot the resulting average trace.")

    parser.add_argument('--verbose', action="store_true", default=False)

    args = parser.parse_args()

    if args.basename == "currdate":
        basename = "cab_dpa_data_" + datetime.datetime.now().isoformat()[:10]
    else:
        basename = args.basename

    gen_traces(args.destdir, basename, args.num_traces, args.num_samples,
                   args.noise_level, args.leakage_level, args.verbose)


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
