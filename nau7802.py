# SPDX-FileCopyrightText: 2023 Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT

"""
nau7802_simpletest.py  2023-01-13 2.0.2  Cedar Grove Maker Studios

Instantiates two NAU7802 channels with default gain of 128 and sample
average count of 2.
"""

import time

import board

from cedargrove_nau7802 import NAU7802


class NAU7802_HELP:
    def zero_channel():
        """Initiate internal calibration for current channel.Use when scale is started,
        a new channel is selected, or to adjust for measurement drift. Remove weight
        and tare from load cell before executing."""
        print(
            "channel {0:1d} calibrate.INTERNAL: {1:5s}".format(
                nau7802.channel, str(nau7802.calibrate("INTERNAL"))
            )
        )
        print(
            "channel {0:1d} calibrate.OFFSET:   {1:5s}".format(
                nau7802.channel, str(nau7802.calibrate("OFFSET"))
            )
        )
        print(f"...channel {nau7802.channel:1d} zeroed")


    def read_raw_value(samples=2):
        """Read and average consecutive raw sample values. Return average raw value."""
        sample_sum = 0
        sample_count = samples
        while sample_count > 0:
            while not nau7802.available():
                pass
            sample_sum = sample_sum + nau7802.read()
            sample_count -= 1
        return int(sample_sum / samples)
