"""Other utilities optimized for this package/project."""
import contextlib
import pkg_resources
from importlib import import_module
import os
from threading import Timer
from subprocess import run, CalledProcessError, PIPE
import pandas as pd
from pathlib import Path


def splitlist(listname, basefilename, n):
    """Split a long list into chunks and save chunks as a text file.

    :param listname: The list that needs to be split.
    :param basefilename: The basefilename of the output text file.
    :param n: The number of chunks to split the list into.
    :return: A list of lists.
    """

    # Split the list into chunks
    chunks = [listname[x:x + n] for x in range(0, len(listname), n)]
    list_group = []
    num_lists = len(chunks)

    # Name and save the lists
    for chunk, num in zip(chunks, range(0, num_lists)):
        listdf = pd.DataFrame(chunk)
        n = basefilename + '_list_' + str(num)
        listdf.to_csv(n + ".txt", index=False, header=None)
        list_group.append(n)
    return list_group


def formatlist(input_list):
    """Remove spaces from list items and turn those spaces into underscores.

    :param input_list: A list that needs formatting.
    :return: A formatted list.
    """

    output_list = []
    for item in input_list:
        item = str(item)
        item = item.replace(" ", "_")
        output_list.append(item)
        return output_list


def makedirectory(path):
    """Creates path/parents and is compatible for python 3.4 and upwards.

    :param path:
    :return:
    """

    exist_ok = True
    if not exist_ok and os.path.isdir(path):
        with contextlib.suppress(OSError):
            Path.mkdir(path, parents=True)


class PackageVersion(object):
    """Get the version of an installed python package."""

    def __init__(self, packagename):
        """Input a package name to return the version.

        :rtype: object
        :param packagename:
        """
        self.packagename = packagename
        self._getversion()

    @property
    def _getversion(self):
        """Get the version of a package.

        :return: Package name and version.
        """

        import_module(self.packagename)
        version = pkg_resources.get_distribution(self.packagename).version
        return "Version {} of {} is installed.".format(version, self.packagename)


def set_paths(parent, **children):
    """Set paths.

    :param parent:
    :param **children:
    """

    raise NotImplementedError("This function is being developed.")


class FunctionRepeater(object):
    """This class repeats a function every desired interval.

    .. note: View https://tinyurl.com/yckgv8m2
    """

    def __init__(self, interval, function, *args, **kwargs):
        """Repeat a function every interval.

        :param interval: Amount of time for function to repeat.
        :param function: Function that needs to repeat.
        :param args:
        :param kwargs:
        """
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        """Time the running of the function."""

        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Start the time."""

        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stop the timer."""

        self._timer.cancel()
        self.is_running = False


def csvtolist(csvfile, column_header='Organism'):
    """Turn a column from a csv file into a list.

    :param csvfile: Name/Path of the csvfile.
    :param column_header: Header of the column.
    :return: A list is returned.
    """

    file = pd.read_csv(csvfile)
    # Create a list name/variable and use list()
    listfromcolumn = list(file[column_header])

    return listfromcolumn


def runcmd(command_string):
    """Run a command string.

    :param command string:
    """

    try:
        cmd = [command_string]  # this is the command
        # Shell MUST be True
        cmd_status = run(cmd, stdout=PIPE, stderr=PIPE, shell=True, check=True)
    except CalledProcessError as err:
        errmsg = err.stderr.decode('utf-8')
        return errmsg
    else:
        if cmd_status.returncode == 0:  # Command was successful.
            # The cmd_status has stdout that must be decoded.
            cmd_stdout = cmd_status.stdout.decode('utf-8')
            return cmd_stdout
        else:  # Unsuccessful. Stdout will be '1'
            failmsg = '%s failed.' % command_string
            return failmsg
