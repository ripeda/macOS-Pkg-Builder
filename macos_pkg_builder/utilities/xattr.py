"""
xattr.py
"""

import subprocess

from . import subprocess_wrapper


class ExtendedAttributes:

    def __init__(self, file: str):
        self._file = file


    def _strip_all_xattr(self) -> bool:
        """
        Strip all extended attributes.
        """
        args = [
            "/usr/bin/xattr",
            "-c",
            self._file,
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            subprocess_wrapper.SubprocessErrorLogging(result).log()
            return False

        return True


    def _strip_xattr(self, key: str) -> bool:
        """
        Strip extended attribute.
        """

        args = [
            "/usr/bin/xattr",
            "-d",
            key,
            self._file,
        ]

        subprocess.run(args, capture_output=True)
        return True


    def strip_xattr(self, key: str = None) -> bool:
        """
        Strip extended attributes.
        """
        if key is None:
            return self._strip_all_xattr()
        return self._strip_xattr(key)