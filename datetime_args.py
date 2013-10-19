#!/usr/bin/env python
#
# Author: Tudor Bosman <tudorb@gmail.com>
# From https://github.com/facebook/tornado/blob/master/tornado/options.py
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import re

# Supported date/time formats in our options
_DATETIME_FORMATS = [
    "%a %b %d %H:%M:%S %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M",
    "%Y%m%d %H:%M:%S",
    "%Y%m%d %H:%M",
    "%Y-%m-%d",
    "%Y%m%d",
    "%H:%M:%S",
    "%H:%M",
]

def parse_datetime(value):
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise Error('Unrecognized date/time format: %r' % value)

_TIMEDELTA_ABBREVS = [
    ('hours', ['h']),
    ('minutes', ['m', 'min']),
    ('seconds', ['s', 'sec']),
    ('milliseconds', ['ms']),
    ('microseconds', ['us']),
    ('days', ['d']),
    ('weeks', ['w']),
]

_TIMEDELTA_ABBREV_DICT = dict(
    (abbrev, full) for full, abbrevs in _TIMEDELTA_ABBREVS
    for abbrev in abbrevs)

_FLOAT_PATTERN = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'

_TIMEDELTA_PATTERN = re.compile(
    r'\s*(%s)\s*(\w*)\s*' % _FLOAT_PATTERN, re.IGNORECASE)

def parse_timedelta(value):
    try:
        sum = datetime.timedelta()
        start = 0
        while start < len(value):
            m = _TIMEDELTA_PATTERN.match(value, start)
            if not m:
                raise Exception()
            num = float(m.group(1))
            units = m.group(2) or 'seconds'
            units = _TIMEDELTA_ABBREV_DICT.get(units, units)
            sum += datetime.timedelta(**{units: num})
            start = m.end()
        return sum
    except Exception:
        raise

