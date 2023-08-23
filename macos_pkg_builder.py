#!/usr/bin/env python3

"""
macOS Package Builder

Designed to simplify package creation through native tooling, ex. pkgbuild, productbuild, etc.
"""

import tempfile
import subprocess

from pathlib import Path

PKGBUILD = "/usr/bin/pkgbuild"


class Packages:

    def __init__(self,
                 pkg_name:               str,
                 pkg_output:             str,
                 pkg_bundle_id:          str = None,
                 pkg_version:            str = "1.0.0",
                 pkg_file_structure:    dict = None,
                 pkg_preinstall_script:  str = None,
                 pkg_postinstall_script: str = None,
                 pkg_install_location:   str = "/",

                ) -> None:
        """
        File Structure:
            {
                # Source: Destination
                "~/Developer/MyApp.app": "/Applications/MyApp.app",
                "~/Developer/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",

            }
        """

        # If all are None, raise an exception.
        if all([pkg_file_structure is None, pkg_preinstall_script is None, pkg_postinstall_script is None]):
            raise Exception("Cannot build a package!")

        self._pkg_project_name       = pkg_name
        self._pkg_project_identifier = pkg_bundle_id if pkg_bundle_id is not None else f"com.{pkg_name.lower()}"
        self._pkg_project_version    = pkg_version
        self._pkg_install_location   = pkg_install_location
        self._pkg_output             = pkg_output
        self._pkg_file_structure     = pkg_file_structure
        self._pkg_preinstall_script  = pkg_preinstall_script
        self._pkg_postinstall_script = pkg_postinstall_script
        self._pkg_file_name          = Path(self._pkg_output).name

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
            print(f"Copying {self._pkg_preinstall_script} to {self._pkg_scripts_directory.joinpath('preinstall')}")
            self._pkg_scripts_directory.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", self._pkg_preinstall_script, self._pkg_scripts_directory.joinpath("preinstall")])
            subprocess.run(["chmod", "+x", self._pkg_scripts_directory.joinpath("preinstall")])

        if self._pkg_postinstall_script is not None:
            print(f"Copying {self._pkg_postinstall_script} to {self._pkg_scripts_directory.joinpath('postinstall')}")
            self._pkg_scripts_directory.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cp", self._pkg_postinstall_script, self._pkg_scripts_directory.joinpath("postinstall")])
            subprocess.run(["chmod", "+x", self._pkg_scripts_directory.joinpath("postinstall")])


    def _prepare_file_structure(self) -> None:
        """
        Adjusts file structure to match pkgbuild requirements.
        """

        if self._pkg_file_structure is not None:
            print(f"Copying files to {self._pkg_build_directory}")
            self._pkg_build_directory.mkdir(parents=True, exist_ok=True)

            for source, destination in self._pkg_file_structure.items():
                if not Path(source).exists():
                    raise Exception(f"Source file does not exist: {source}")

                internal_destination = Path(f"{self._pkg_build_directory}{destination}")

                if not internal_destination.parent.exists():
                    internal_destination.parent.mkdir(parents=True, exist_ok=True)

                subprocess.run(["cp", "-R", source, internal_destination])


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


    def build(self) -> None:
        """
        Build the application package.
        """
        if Path(self._pkg_output).exists():
            print(f"Removing existing package: {self._pkg_output}")
            Path(self._pkg_output).unlink()

        self._prepare_scripts()
        self._prepare_file_structure()
        if self._build_pkg() is False:
            print("Package build failed.")
            return

        subprocess.run(["cp", self._pkg_build_directory.parent / self._pkg_file_name, self._pkg_output])
        print(f"Package built: {self._pkg_output}")


if __name__ == "__main__":
    test_suite = Packages(
        pkg_name="MyApp-Installer",
        pkg_output="Sample.pkg",
        pkg_bundle_id="com.myapp.installer",
        pkg_file_structure={
            "Samples/MyApp/MyApp.app": "/Applications/MyApp.app",
            "Samples/MyApp/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
        },
        pkg_preinstall_script="Samples/MyApp/MyPreinstall.sh",
        pkg_postinstall_script="Samples/MyApp/MyPostinstall.sh",
    )

    test_suite.build()