#!/usr/bin/env python
#
# Author: Tudor Bosman <tudorb@gmail.com>
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

"""
Tool to check ZFS pool status and print a summary report.
"""

import argparse
import collections
import logging
import sys

from zfs_utils import *

HEALTHY = "HEALTHY"
DEGRADED = "DEGRADED"
UNAVAILABLE = "UNAVAILABLE"

pool_statuses = [HEALTHY, DEGRADED, UNAVAILABLE]

_POOL_STATUS_MAP = {
    "DEGRADED":     DEGRADED,
    "FAULTED":      UNAVAILABLE,
    "OFFLINE":      HEALTHY,
    "ONLINE":       HEALTHY,
    "UNAVAIL":      UNAVAILABLE,
}

def get_pool_status(health, allow_removable):
    if health == "REMOVED":
        status = HEALTHY if allow_removable else UNAVAILABLE
    else:
        status = _POOL_STATUS_MAP.get(health)
        if status is None:
            logging.error("Unknown pool health %s", health)
            status = pool_status.UNAVAILABLE  # better safe than sorry
    return status

_LOG_LEVELS = {
    HEALTHY:     logging.INFO,
    DEGRADED:    logging.WARNING,
    UNAVAILABLE: logging.ERROR,
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all",
                        action="store_true",
                        help="Check health for all pools")
    parser.add_argument("--removable",
                        action="store_true",
                        help="Allow pools in REMOVED status (removable media?")
    parser.add_argument("pool",
                        nargs="*",
                        help="Pool to check status for")

    # TODO(tudor): logging configured from command-line flags
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))

    args = parser.parse_args()
                        
    if args.all:
        pools = []  # default option for zpool_list_health
    elif not args.pool:
        sys.exit(0)
    else:
        pools = args.pool

    status_counts = collections.Counter()

    pool_health_map = zpool_list_health(*pools)
    max_log_level = logging.INFO
    for pool, health in pool_health_map.iteritems():
        status = get_pool_status(health, allow_removable=args.removable)

        log_level = _LOG_LEVELS[status]
        if log_level > max_log_level:
            max_log_level = log_level

        logging.log(log_level, "Pool \"%s\": %s (%s)",
                    pool, str(status).lower(), health)

        status_counts[status] += 1

    summary = ["%d %s" % (status_counts[status], status.lower())
               for status in pool_statuses]
    summary = ", ".join(summary)
    logging.log(max_log_level, "Summary: %s", summary)

    if status_counts[UNAVAILABLE] > 0:
        sys.exit(2)
    elif status_counts[DEGRADED] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
