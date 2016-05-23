# tracegen #
A tool for generating synthetic traces with side-channel leakage.


## Introduction ##
Power based side-channel leakage requires traces and a tool for
analyzing the traces and extracting information related to the internal
state of the test object.

There are a number of traces available. But for verifying a side-channel
analysis tool, having data controlled by the developer allows for
reliable testing of the analysis tool separate from a real target.

The tracegen tool is able to generate a given number of traces, each
with a given number of samples. Additionally, side information (for
example cipher text) related to the traces can be generated.

How uncorrelated variance is modified can be controlled. Variance in
correlated effect on samples (the spread of effect over one or more
samples) can be controlled. The target model can be controlled.


## Implementation ##
The initial version modles uncorrelated variance as zero. The target
model is DES final round XOR operation.
