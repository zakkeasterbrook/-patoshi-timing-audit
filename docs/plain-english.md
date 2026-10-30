# What was wrong, in plain English

The published test was supposed to ask: after two consecutive blocks labelled Patoshi, how quickly does a block outside that list follow?

Consider three timestamped entries in a logbook. The test needs the difference between the second and third entries. The program accidentally subtracts the first entry's time from the third. That includes an extra recorded interval; it does not measure how long mining actually took.

There is a second consequence: the rule for choosing examples checks whether the second mark is less than ten minutes after the first. Because both variables contain the first time, that check always passes. Separate sequence-tracking mistakes also leave out eligible examples.

## A real example

Blocks 263, 264 and 265 have header times of 00:10:21, 00:19:40 and 00:20:51 UTC on 13 January 2009.

The first gap is 9 minutes 19 seconds. The following gap is 1 minute 11 seconds. The original code reports 10 minutes 30 seconds for that following gap.

You can reproduce the example with `python scripts/demo.py`.

## Why it matters

The article reported only five short gaps among 1,881 selected cases. Implementing its stated selection and measurement rules produces 276 among 754 cases. Both counts include negative timestamp differences. Short recorded gaps are common in the corrected test.

The denominator changes because fixing the selection changes which examples qualify. This is not a claim that 271 observations were simply added to the same sample.

## The finding

The published program does not compute its stated timing statistic. The reported scarcity of short following-block timestamp gaps does not survive a correct implementation of that test.

That is a concrete, checkable finding. It does not establish who mined the blocks, how much bitcoin anyone owns, or whether the miner slept between blocks. The wider Patoshi pattern has several kinds of evidence; correcting this one test does not erase them.

## Why the timestamps need care

A block includes a time supplied by its miner. Different miners can have different clocks, so one block’s recorded time can even be earlier than its parent’s. A “negative gap” is a clock observation, not time travel.

All counts in this project refer to those recorded times. The repository includes the data and complete calculations so readers can challenge the result directly.
