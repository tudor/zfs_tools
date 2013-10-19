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
Miscellaneous ZFS utilites; implemented by executing zfs and zpool.
"""

import subprocess

def noun_count(n, singular, plural=None):
    """Generate a phrase suitable for displaying N counts of a noun, given
       the noun's singular and plural forms.  (If the plural form is not
       given, the standard English rule of adding an "s" is used)
       noun_count(1, "disk") -> "1 disk"
       noun_count(2, "disk") -> "2 disks"
    """
    if plural is None:
        plural = singular + "s"
    return "%d %s" % (n, singular if n == 1 else plural)


def execute(*args):
    """Execute a command and read its stdout, returning it as an array
       (one element per line)"""
    proc = subprocess.Popen(args, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, " ".join(args))
    return output.splitlines()


def zfs_list_filesystems():
    """List all ZFS filesystems."""
    return execute("zfs", "list", "-tfilesystem", "-H", "-oname")


def zfs_get_property(fs, property):
    """Retrieve a ZFS property on a filesystem."""
    return execute("zfs", "get", "-H", "-ovalue", property, fs)[0]


def zfs_create_snapshot(fs, snapshot):
    """Create a ZFS snapshot."""
    execute("zfs", "snapshot", "%s@%s" % (fs, snapshot))


def zfs_delete_snapshot(fs, snapshot):
    """Delete a ZFS snapshot."""
    execute("zfs", "destroy", "%s@%s" % (fs, snapshot))


def zpool_get_health(pool):
    """Get the health of a ZFS pool."""
    return execute("zpool", "list", "-H", "-ohealth", pool)[0]


def zpool_is_online(pool):
    """Check whether a pool is online."""
    return zpool_get_health(pool) == "ONLINE"


def zpool_list_health(*pools):
    """List health for all (default) or the given pools; return a dictionary
       {pool_name: health}"""
    ret = {}
    for line in execute("zpool", "list", "-H", "-oname,health", *pools):
        name, health = line.split("\t")
        ret[name] = health
    return ret

