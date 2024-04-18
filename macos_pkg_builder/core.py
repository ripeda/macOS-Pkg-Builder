#!/usr/bin/env python3

"""
macOS Package Builder

Designed to simplify package creation through native tooling, ex. pkgbuild, productbuild, etc.
"""

import logging

from pathlib import Path

from .flat_pkg import FlatPackage
from .distribution_pkg import DistributionPackage


class Packages:

    def __init__(self,
                 pkg_output:              str,
                 pkg_bundle_id:           str,
                 pkg_version:             str = "1.0.0",
                 pkg_install_location:    str = "/",
                 pkg_allow_relocation:   bool = True,
                 pkg_file_structure:     dict = None,
                 pkg_preinstall_script:   str = None,
                 pkg_preflight_script:    str = None,
                 pkg_postinstall_script:  str = None,
                 pkg_postflight_script:   str = None,
                 pkg_script_resources:   list = None,
                 pkg_signing_identity:    str = None,
                 pkg_as_distribution:    bool = False,
                 pkg_title:               str = None,
                 pkg_welcome:             str = None,
                 pkg_readme:              str = None,
                 pkg_license:             str = None,
                 pkg_background:          str = None,
                 pkg_background_dark:     str = None,
                ) -> None:
        """
        pkg_output:             Path to where the package will be saved.
                                Required.

        pkg_bundle_id:          Bundle ID of the package.
                                Required.

        pkg_version:            Version of the package.
                                Default: 1.0.0
                                Optional.

        pkg_install_location:   Location where the package will be installed.
                                Default: /
                                Optional.

        pkg_allow_relocation:   Allow the embedded application to be installed where the user has an existing copy (outside expected install location)
                                Requires a valid bundle to be provided in 'pkg_file_structure' (ex. app, plugin, etc.)
                                Default: True
                                Optional.

        pkg_file_structure:     File structure of the package.
                                Configured as a dictionary, where the key is the source file and the value is the destination.
                                Default: None
                                Optional if preinstall or postinstall scripts are provided.

        pkg_preinstall_script:  Path to the preinstall script.
                                Default: None
                                Optional.

        pkg_preflight_script:   Path to the preflight script.
                                Default: None
                                Optional.

        pkg_postinstall_script: Path to the postinstall script.
                                Default: None
                                Optional.

        pkg_postflight_script:  Path to the postflight script.
                                Default: None
                                Optional.

        pkg_script_resources:   List of additional scripts to be included in the package.
                                This is primarily for pre/postinstall scripts that need additional resources present next to them.
                                ex. Shipping 'desktoppr' with a wallpaper, and have the postinstall script set the wallpaper.
                                Default: None
                                Optional.

        pkg_signing_identity:   Signing identity to use when signing the package.
                                If missing, no signing will be performed.
                                Default: None
                                Optional.

        pkg_as_distribution:    Convert the package to a product archive.
                                Default: False
                                Optional.

        pkg_title:              Title of the distribution package.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        pkg_welcome:            Content of the WELCOME file as markdown.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        pkg_readme:             Content of the README file as markdown.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        pkg_license:            Content of the LICENSE file as markdown.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        pkg_background:         Path to the background image for the distribution package.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        pkg_background_dark:    Path to the dark background image for the distribution package.
                                If not provided, the light background will be used.
                                Default: None
                                Optional. Requires 'pkg_as_distribution' to be True.

        File Structure:
            {
                # Source: Destination
                "~/Developer/MyApp.app": "/Applications/MyApp.app",
                "~/Developer/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
            }
        """

        self._pkg_project_identifier = pkg_bundle_id
        self._pkg_project_version    = pkg_version
        self._pkg_install_location   = pkg_install_location
        self._pkg_output             = pkg_output
        self._pkg_file_structure     = pkg_file_structure
        self._pkg_preinstall_script  = pkg_preinstall_script
        self._pkg_preflight_script   = pkg_preflight_script
        self._pkg_postinstall_script = pkg_postinstall_script
        self._pkg_postflight_script  = pkg_postflight_script
        self._pkg_file_name          = Path(self._pkg_output).name
        self._pkg_allow_relocation   = pkg_allow_relocation
        self._pkg_script_resources   = pkg_script_resources
        self._pkg_signing_identity   = pkg_signing_identity
        self._pkg_as_distribution    = pkg_as_distribution
        self._pkg_title              = pkg_title
        self._pkg_welcome            = pkg_welcome
        self._pkg_readme             = pkg_readme
        self._pkg_license            = pkg_license
        self._pkg_background         = pkg_background
        self._pkg_background_dark    = pkg_background_dark

        _requires_distribution = [
            self._pkg_title,
            self._pkg_welcome,
            self._pkg_readme,
            self._pkg_license,
            self._pkg_background,
            self._pkg_background_dark
        ]

        if self._pkg_as_distribution is False and any(_requires_distribution):
            raise Exception("Distribution files require 'pkg_as_distribution' to be True.")


    def build(self) -> bool:
        """
        Build the application package.
        """

        result = FlatPackage(
            pkg_output=self._pkg_output,
            pkg_bundle_id=self._pkg_project_identifier,
            pkg_version=self._pkg_project_version,
            pkg_install_location=self._pkg_install_location,
            pkg_allow_relocation=self._pkg_allow_relocation,
            pkg_file_structure=self._pkg_file_structure,
            pkg_preinstall_script=self._pkg_preinstall_script,
            pkg_preflight_script=self._pkg_preflight_script,
            pkg_postinstall_script=self._pkg_postinstall_script,
            pkg_postflight_script=self._pkg_postflight_script,
            pkg_script_resources=self._pkg_script_resources,
            pkg_signing_identity=self._pkg_signing_identity
        ).build()

        if result is False:
            return False

        if self._pkg_as_distribution is False:
            return True

        logging.info("Converting to distribution package.")

        result = DistributionPackage(
            pkg_output=self._pkg_output,
            pkg_inputs=[self._pkg_output],
            pkg_bundle_id=self._pkg_project_identifier,
            pkg_version=self._pkg_project_version,
            pkg_title=self._pkg_title,
            pkg_welcome=self._pkg_welcome,
            pkg_readme=self._pkg_readme,
            pkg_license=self._pkg_license,
            pkg_background=self._pkg_background,
            pkg_background_dark=self._pkg_background_dark,
            pkg_signing_identity=self._pkg_signing_identity
        ).build()

        return result


