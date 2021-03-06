"""Base FTP module for connecting to FTP servers."""
from ftplib import FTP, error_perm
import os
import contextlib

from OrthoEvol.Tools.otherutils import FunctionRepeater


class BaseFTPClient(object):
    """The BaseFTP class provides basic functions for managing ftp clients.

    .. seealso:: :class:`NcbiFTPClient`
    """

    def __init__(self, ftpsite, email, keepalive=False, debug_lvl=0):
        """Connect to a ftp site using an email address.

        :param ftpsite: Address of the ftp site you want to connect to.
        :param email: Input your email address.
        :param keepalive: Flag to determine whether to keepalive the connection
                          (Default value = False)
        :type keepalive: bool
        :param debug_lvl: Verbosity level for debugging ftp connection
                          (Default value = 0)
        :type debug_lvl: int
        """
        self._ftpsite = ftpsite
        self._email = email
        self._debug_lvl = debug_lvl
        self.ftp = self._login()
        self.__keepalive = keepalive

        if self.__keepalive:
            self._voidcmd_repeat, self._filetransfer_repeat = self._keepalive()

    def _keepalive(self):
        """Check to see if the FTP connection still exists using ftp.voidcmd

        Also, creates a filetransfer to prevent file transfer timeout.

        .. warning:: :func:`_keepalive` is not well tested.
        Avoid using it if possible.
        """

        voidcmd = FunctionRepeater(5, self.ftp.voidcmd, 'NOOP')
        filetransfer = FunctionRepeater(5, self._filetransfer, 'README.ftp')

        return voidcmd, filetransfer

    def _login(self):
        """Connect to the FTP server anonymously."""

        with contextlib.suppress(error_perm):
            ftp = FTP(self._ftpsite, timeout=600)
            ftp.login(user='anonymous', passwd=self._email)
            ftp.voidcmd('NOOP')
            ftp.set_debuglevel(self._debug_lvl)

        return ftp

    def close_connection(self):
        """Close the ftp connection."""

        self.ftp.close()

        if self.__keepalive:
            self._voidcmd_repeat.stop()
            self._filetransfer_repeat.stop()

    def _filetransfer(self, filename):
        """Mimics a file transfer to prevent transfer time out.

        :param filename: Path of file to download.
        """

        print("WAIT: Keeping connection open by transferring file.")
        current_path = self.ftp.pwd()
        self.ftp.cwd('/')

        with open(filename, 'wb') as local_file:
            self.ftp.retrbinary('RETR %s' % filename, local_file.write)

        os.remove(filename)
        self.ftp.cwd(current_path)  # Return to starting path
        print("You may now resume your work.")
