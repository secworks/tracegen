#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=======================================================================
#
# tracegen.py
# -----------
# Tool for generating synthetic traces with side-channel leakage.
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
import cPickle as pickle
import datetime

import matplotlib.pyplot as plt
import numpy
import ujson


#-------------------------------------------------------------------
# Defines.
#-------------------------------------------------------------------


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
    parser.add_argument('--verbose', action="store_true", default=False)
    parser.add_argument('-n' '--traces', action="store", dest="num_traces",
                            type=int, help="Number of traces to geneate. Default 1000", default=1000)
    parser.add_argument('-s' '--samples', action="store", dest="num_traces",
                            type=int, help="Number of samples in a trace. Default 1000", default=1000)
    parser.add_argument('-p', '--plot', action="store_true", dest='do_plot', default=False,
                            help="Plot the resulting average trace.")
    args = parser.parse_args()


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
