"""
signing.py: Package Signing Utilities

Note that while pkgbuild and productbuild support passing the signing identity as an argument,
separating this step allows for easier debugging and testing.

If a noticeable performance hit is observed, consider merging this step with the package building
"""

import logging
import subprocess

from pathlib import Path

from . import subprocess_wrapper


PRODUCTSIGN: str = "/usr/bin/productsign"
SECURITY:    str = "/usr/bin/security"


class SignPackage:

    def __init__(self, pkg: str, identity: str) -> None:
        self.pkg = pkg
        self.identity = identity


    def _is_identity_valid(self) -> bool:
        """
        Check if the provided signing identity is valid.
        """

        args = [
            SECURITY,
            "find-identity",
            "-v",
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            subprocess_wrapper.SubprocessErrorLogging(result).log()
            return False

        if self.identity not in result.stdout.decode("utf-8"):
            logging.info(f"Signing identity not found: {self.identity}")
            return False

        return True


    def sign(self) -> bool:
        """
        Sign package.
        """

        if self._is_identity_valid() is False:
            return False

        args = [
            PRODUCTSIGN,
            "--sign", self.identity,
            self.pkg,
            str(self.pkg) + ".signed",
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            subprocess_wrapper.SubprocessErrorLogging(result).log()
            return False

        # Replace the original package with the signed one.
        Path(self.pkg).unlink()
        Path(str(self.pkg) + ".signed").rename(self.pkg)

        return True