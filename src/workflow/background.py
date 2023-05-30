#!/usr/bin/env python3

"""This module provides an API to run commands in background processes.

Combine with the :ref:`caching API <caching-data>` to work from cached data
while you fetch fresh data in the background.

See :ref:`the User Manual <background-processes>` for more information
and examples.
"""

import os
import pickle
import signal
import subprocess
import sys

from workflow import Workflow

__all__ = ["is_running", "run_in_background"]

wf = Workflow()


def _arg_cache(name):
    """Return path to pickle cache file for arguments.

    :param name: name of task
    :type name: ``str``
    :returns: Path to cache file
    :rtype: ``str`` filepath

    """
    return wf.cachefile(name + ".argcache")


def _pid_file(name):
    """Return path to PID file for ``name``.

    :param name: name of task
    :type name: ``str``
    :returns: Path to PID file for task
    :rtype: ``str`` filepath

    """
    return wf.cachefile(name + ".pid")


def _process_exists(pid):
    """Check if a process with PID ``pid`` exists.

    :param pid: PID to check
    :type pid: ``int``
    :returns: ``True`` if process exists, else ``False``
    :rtype: ``Boolean``

    """
    try:
        os.kill(pid, 0)
    except OSError:  # not running
        return False
    return True


def _job_pid(name):
    """Get PID of job or `None` if job does not exist.

    Args:
        name (str): Name of job.

    Returns:
        int: PID of job process (or `None` if job doesn't exist).
    """
    pidfile = _pid_file(name)

    if os.path.exists(pidfile):
        with open(pidfile, "rb") as f:
            read = f.read()
            pid = int.from_bytes(read, sys.byteorder)

            if _process_exists(pid):
                return pid

        os.unlink(pidfile)
    return None


def is_running(name):
    """Test whether task ``name`` is currently running.

    :param name: name of task
    :type name: str
    :returns: ``True`` if task with name ``name`` is running, else ``False``
    :rtype: bool

    """
    if _job_pid(name) is not None:
        return True

    return False


def _background(
    pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"
):  # pragma: no cover
    """Fork the current process into a background daemon.

    :param pidfile: file to write PID of daemon process to.
    :type pidfile: filepath
    :param stdin: where to read input
    :type stdin: filepath
    :param stdout: where to write stdout output
    :type stdout: filepath
    :param stderr: where to write stderr output
    :type stderr: filepath

    """

    def _fork_and_exit_parent(errmsg, wait=False, write=False):
        try:
            pid = os.fork()
            if pid > 0:
                if write:  # write PID of child process to `pidfile`
                    tmp = pidfile + ".tmp"

                    with open(tmp, "wb") as f:
                        f.write(pid.to_bytes(4, sys.byteorder))

                    os.rename(tmp, pidfile)
                if wait:  # wait for child process to exit
                    os.waitpid(pid, 0)
                os._exit(0)
        except OSError as err:
            wf.logger.critical("%s: (%d) %s", errmsg, err.errno, err.strerror)
            raise err

    # Do first fork and wait for second fork to finish.
    _fork_and_exit_parent("fork #1 failed", wait=True)

    # Decouple from parent environment.
    os.chdir(wf.workflowdir)
    os.setsid()

    # Do second fork and write PID to pidfile.
    _fork_and_exit_parent("fork #2 failed", write=True)

    # Now I am a daemon!
    # Redirect standard file descriptors.
    with open(stdin, "r", 1, encoding="utf-8") as stdin_fd:
        if hasattr(sys.stdin, "fileno"):
            os.dup2(stdin_fd.fileno(), sys.stdin.fileno())

    with open(stdout, "a+", 1, encoding="utf-8") as stdout_fd:
        if hasattr(sys.stdout, "fileno"):
            os.dup2(stdout_fd.fileno(), sys.stdout.fileno())

    with open(stderr, "a+", 1, encoding="utf-8") as stderr_fd:
        if hasattr(sys.stderr, "fileno"):
            os.dup2(stderr_fd.fileno(), sys.stderr.fileno())


def kill(name, sig=signal.SIGTERM):
    """Send a signal to job ``name`` via :func:`os.kill`.

    Args:
        name (str): Name of the job
        sig (int, optional): Signal to send (default: SIGTERM)

    Returns:
        bool: `False` if job isn't running, `True` if signal was sent.
    """
    pid = _job_pid(name)
    if pid is None:
        return False

    os.kill(pid, sig)
    return True


def run_in_background(name, args, **kwargs):
    r"""Cache arguments then call this script again via :func:`subprocess.run`.

    :param name: name of job
    :type name: str
    :param args: arguments passed as first argument to :func:`subprocess.run`
    :param \**kwargs: keyword arguments to :func:`subprocess.run`
    :returns: exit code of sub-process
    :rtype: int

    When you call this function, it caches its arguments and then calls
    ``background.py`` in a subprocess. The Python subprocess will load the
    cached arguments, fork into the background, and then run the command you
    specified.

    This function will return as soon as the ``background.py`` subprocess has
    forked, returning the exit code of *that* process (i.e. not of the command
    you're trying to run).

    If that process fails, an error will be written to the log file.

    If a process is already running under the same name, this function will
    return immediately and will not run the specified command.

    """
    if is_running(name):
        wf.logger.info("[%s] job already running", name)
        return None

    argcache = _arg_cache(name)

    # Cache arguments
    with open(argcache, "wb") as f:
        pickle.dump({"args": args, "kwargs": kwargs}, f)
        wf.logger.debug("[%s] command cached: %s", name, argcache)

    # Call this script
    cmd = ["python3", "-m", "workflow.background", name]
    wf.logger.debug("[%s] passing job to background runner: %r", name, cmd)
    retcode = subprocess.run(cmd, check=True).returncode

    if retcode:  # pragma: no cover
        wf.logger.error("[%s] background runner failed with %d", name, retcode)
    else:
        wf.logger.debug("[%s] background job started", name)

    return retcode


def main(wf):  # pragma: no cover  # pylint: disable=redefined-outer-name
    """Run command in a background process.

    Load cached arguments, fork into background, then call
    :meth:`subprocess.run` with cached arguments.

    """
    name = wf.args[0]
    argcache = _arg_cache(name)

    if not os.path.exists(argcache):
        msg = f"[{name}] command cache not found: {argcache}"
        wf.logger.critical(msg)
        raise IOError(msg)

    # Fork to background and run command
    pidfile = _pid_file(name)
    _background(pidfile)

    # Load cached arguments
    with open(argcache, "rb") as f:
        data = pickle.load(f)

    # Cached arguments
    args = data["args"]
    kwargs = data["kwargs"]

    # Delete argument cache file
    os.unlink(argcache)

    try:
        # Run the command
        wf.logger.debug("[%s] running command: %r", name, args)

        retcode = subprocess.run(args, **kwargs, check=True).returncode

        if retcode:
            wf.logger.error("[%s] command failed with status %d", name, retcode)
    finally:
        os.unlink(pidfile)

    wf.logger.debug("[%s] job complete", name)


if __name__ == "__main__":  # pragma: no cover
    wf.run(main)
