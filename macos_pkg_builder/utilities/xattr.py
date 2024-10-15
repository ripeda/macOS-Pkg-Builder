"""
xattr.py
"""

import logging
import subprocess

from . import subprocess_wrapper


class ExtendedAttributes:

    def __init__(self, file: str):
        self._file = file


    def _get_xattr(self) -> dict:
        """
        Get extended attributes.
        """
        args = [
            "/usr/bin/xattr",
            "-l",
            self._file,
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            subprocess_wrapper.SubprocessErrorLogging(result).log()
            return {}

        xattr = {}
        for line in result.stdout.decode("utf-8").split("\n"):
            if not line:
                continue
            key, values = line.split(":", 1)
            if key not in xattr:
                xattr[key] = []
            xattr[key].append(values.strip())

        return xattr


    def get_xattr(self) -> dict:
        """
        Get extended attributes.
        """
        return self._get_xattr()


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
        if key not in self._get_xattr():
            logging.error(f"Extended attribute not found: {key}")
            return False

        args = [
            "/usr/bin/xattr",
            "-d",
            key,
            self._file,
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            subprocess_wrapper.SubprocessErrorLogging(result).log()
            return False

        return True


    def strip_xattr(self, key: str = None) -> bool:
        """
        Strip extended attributes.
        """
        if key is None:
            return self._strip_all_xattr()
        return self._strip_xattr(key)