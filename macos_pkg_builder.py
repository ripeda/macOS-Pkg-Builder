#!/usr/bin/env python3

"""
macOS Package Builder

Designed to simplify package creation through native tooling, ex. pkgbuild, productbuild, etc.
"""

import tempfile
import plistlib
import subprocess

from pathlib import Path


PKGBUILD = "/usr/bin/pkgbuild"


class Packages:

    def __init__(self,
                 pkg_output:              str,
                 pkg_bundle_id:           str,
                 pkg_version:             str = "1.0.0",
                 pkg_install_location:    str = "/",
                 pkg_allow_relocation:   bool = True,
                 pkg_file_structure:     dict = None,
                 pkg_preinstall_script:   str = None,
                 pkg_postinstall_script:  str = None,
                ) -> None:
        """
        pkg_output:             Path to where the package will be saved.

        pkg_bundle_id:          Bundle ID of the package.

        pkg_version:            Version of the package.
                                Default: 1.0.0

        pkg_install_location:   Location where the package will be installed.
                                Default: /
                                Optional.

        pkg_allow_relocation:   Allow the embedded application to be installed where the user has an existing copy (outside expected install location)
                                Requires a valid bundle to be provided in 'pkg_file_structure' (ex. app, plugin, etc.)
                                Default: True

        pkg_file_structure:     File structure of the package.
                                Configured as a dictionary, where the key is the source file and the value is the destination.
                                Default: None
                                Optional if preinstall or postinstall scripts are provided.

        pkg_preinstall_script:  Path to the preinstall script.
                                Default: None
                                Optional.

        pkg_postinstall_script: Path to the postinstall script.
                                Default: None
                                Optional.

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
        self._pkg_postinstall_script = pkg_postinstall_script
        self._pkg_file_name          = Path(self._pkg_output).name
        self._pkg_allow_relocation   = pkg_allow_relocation

        self._pkg_temp_directory     = tempfile.TemporaryDirectory()
        self._pkg_temp_directory     = Path(self._pkg_temp_directory.name)
        self._pkg_build_directory    = Path(self._pkg_temp_directory, "build")
        self._pkg_scripts_directory  = Path(self._pkg_temp_directory, "scripts")
        self._pkg_output_directory   = Path(self._pkg_temp_directory, "output")


    def _prepare_scripts(self) -> None:
        """
        Adjusts naming and permissions of scripts to match pkgbuild requirements.
        """

        if self._pkg_preinstall_script is not None:
            self._pkg_scripts_directory.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", self._pkg_preinstall_script, self._pkg_scripts_directory.joinpath("preinstall")])
            subprocess.run(["chmod", "+x", self._pkg_scripts_directory.joinpath("preinstall")])

        if self._pkg_postinstall_script is not None:
            self._pkg_scripts_directory.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", self._pkg_postinstall_script, self._pkg_scripts_directory.joinpath("postinstall")])
            subprocess.run(["chmod", "+x", self._pkg_scripts_directory.joinpath("postinstall")])


    def _prepare_file_structure(self) -> None:
        """
        Adjusts file structure to match pkgbuild requirements.
        """

        if self._pkg_file_structure is None:
            return

        self._pkg_build_directory.mkdir(parents=True, exist_ok=True)

        for source, destination in self._pkg_file_structure.items():
            if not Path(source).exists():
                raise Exception(f"Source file does not exist: {source}")

            internal_destination = Path(f"{self._pkg_build_directory}{destination}")

            if not internal_destination.parent.exists():
                internal_destination.parent.mkdir(parents=True, exist_ok=True)

            subprocess.run(["cp", "-R", source, internal_destination])


    def _generate_component_file(self) -> None:
        """
        Generate a component file to prevent the relocation of the embedded application(s).
        """

        bundle=""
        file = self._pkg_build_directory.parent / "component.plist"

        # Find anything with an Info.plist embedded, needs to be a valid bundle for pkgbuild.
        for source, destination in self._pkg_file_structure.items():

            if Path(source, "Contents", "Info.plist").exists():
                bundle = destination
                break

        contents = [{
            "BundleHasStrictIdentifier": True,
            "BundleIsRelocatable": self._pkg_allow_relocation,
            "BundleIsVersionChecked": True,
            "BundleOverwriteAction": "upgrade",
            "RootRelativeBundlePath": bundle,
        }]
        plistlib.dump(contents, file.open("wb"))


    def _generate_pkg_arguments(self) -> list:
        """
        Generate pkgbuild arguments according to the provided configuration.
        """

        args = [
            PKGBUILD,
            "--identifier", self._pkg_project_identifier,
            "--version", self._pkg_project_version,
            "--install-location", self._pkg_install_location,
        ]

        if self._pkg_scripts_directory.exists():
            args.extend(["--scripts", self._pkg_scripts_directory])

        if self._pkg_file_structure is not None:
            args.extend(["--root", self._pkg_build_directory])
            if self._pkg_allow_relocation is False:
                self._generate_component_file()
                args.extend(["--component-plist", self._pkg_build_directory.parent / "component.plist"])
        else:
            args.extend(["--nopayload"])


        args.extend([self._pkg_build_directory.parent / self._pkg_file_name])

        return args


    def _build_pkg(self) -> bool:
        """
        Build the application package.
        """
        result = subprocess.run(self._generate_pkg_arguments(), capture_output=True)
        if result.returncode != 0:
            print(result.stderr.decode("utf-8"))
            return False

        return True


    def build(self) -> bool:
        """
        Build the application package.
        """

        if all([self._pkg_file_structure is None, self._pkg_preinstall_script is None, self._pkg_postinstall_script is None]):
            raise Exception("Cannot build a package!")

        if Path(self._pkg_output).exists():
            print(f"Removing existing package: {self._pkg_output}")
            Path(self._pkg_output).unlink()

        self._prepare_scripts()
        self._prepare_file_structure()
        if self._build_pkg() is False:
            print("Package build failed.")
            return False

        if not Path(self._pkg_output).parent.exists():
            Path(self._pkg_output).mkdir(parents=True, exist_ok=True)

        subprocess.run(["cp", self._pkg_build_directory.parent / self._pkg_file_name, self._pkg_output])
        print(f"Package built: {self._pkg_output}")
        return True


if __name__ == "__main__":

    test_suites = [
        Packages(
            pkg_output="Sample-Install.pkg",
            pkg_bundle_id="com.myapp.installer",
            pkg_file_structure={
                ".Samples/MyApp/MyApp.app": "/Applications/MyApp.app",
                ".Samples/MyApp/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
            },
            pkg_preinstall_script=".Samples/MyApp/MyPreinstall.sh",
            pkg_postinstall_script=".Samples/MyApp/MyPostinstall.sh",
        ),
        Packages(
            pkg_output="Sample-Uninstall.pkg",
            pkg_bundle_id="com.myapp.uninstaller",
            pkg_preinstall_script=".Samples/MyUninstaller/MyPreinstall.sh",
        ),
    ]

    for test_suite in test_suites:
        if test_suite.build() is False:
            print("Package build failed.")
            exit(1)
