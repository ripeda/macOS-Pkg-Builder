#!/usr/bin/env python3

"""
macOS Package Builder

Designed to simplify package creation through native tooling, ex. pkgbuild, productbuild, etc.
"""

import logging
import tempfile
import plistlib
import subprocess

from pathlib import Path


PKGBUILD:     str = "/usr/bin/pkgbuild"
PRODUCTBUILD: str = "/usr/bin/productbuild"
PRODUCTSIGN:  str = "/usr/bin/productsign"
SECURITY:     str = "/usr/bin/security"


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
                 pkg_script_resources:   list = None,
                 pkg_signing_identity:    str = None,
                 pkg_as_distribution:    bool = False,
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

        pkg_script_resources:   List of additional scripts to be included in the package.
                                This is primarily for pre/postinstall scripts that need additional resources present next to them.
                                ex. Shipping 'desktoppr' with a wallpaper, and have the postinstall script set the wallpaper.

        pkg_signing_identity:   Signing identity to use when signing the package.
                                If missing, no signing will be performed.

        pkg_as_distribution:    Convert the package to a product archive.
                                Default: False

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
        self._pkg_script_resources   = pkg_script_resources
        self._pkg_signing_identity   = pkg_signing_identity
        self._pkg_as_distribution    = pkg_as_distribution

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

        if self._pkg_script_resources is not None:
            for resources in self._pkg_script_resources:
                subprocess.run(["cp", resources, self._pkg_scripts_directory])
                subprocess.run(["chmod", "+x", self._pkg_scripts_directory.joinpath(Path(resources).name)])


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
            logging.info(result.stderr.decode("utf-8"))
            return False

        return True


    def _is_identity_valid(self) -> bool:
        """
        Check if the provided signing identity is valid.
        """
        if self._pkg_signing_identity is None:
            return False

        args = [
            SECURITY,
            "find-identity",
            "-v",
        ]

        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            logging.info(result.stderr.decode("utf-8"))
            return False

        if self._pkg_signing_identity not in result.stdout.decode("utf-8"):
            logging.info(f"Signing identity not found: {self._pkg_signing_identity}")
            return False

        return True


    def _sign_pkg(self) -> bool:
        """
        Sign application package.
        """
        if self._pkg_signing_identity is None:
            return True

        if self._is_identity_valid() is False:
            return False

        args = [
            PRODUCTSIGN,
            "--sign", self._pkg_signing_identity,
            self._pkg_build_directory.parent / self._pkg_file_name,
            self._pkg_build_directory.parent / Path(self._pkg_file_name + ".signed")
        ]
        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            logging.info(result.stderr.decode("utf-8"))
            return False

        # Replace the original package with the signed one.
        Path(self._pkg_build_directory.parent / self._pkg_file_name).unlink()
        Path(self._pkg_build_directory.parent / Path(self._pkg_file_name + ".signed")).rename(self._pkg_build_directory.parent / self._pkg_file_name)

        return True


    def _convert_to_product_archive(self) -> bool:
        """
        Convert the package to a product archive.
        """
        if self._pkg_as_distribution is False:
            return True

        args = [
            PRODUCTBUILD,
            "--package", self._pkg_build_directory.parent / self._pkg_file_name,
            self._pkg_build_directory.parent / Path(self._pkg_file_name + ".product")
        ]
        result = subprocess.run(args, capture_output=True)
        if result.returncode != 0:
            logging.info(result.stderr.decode("utf-8"))
            return False

        # Replace the original package with the product archive.
        Path(self._pkg_build_directory.parent / self._pkg_file_name).unlink()
        Path(self._pkg_build_directory.parent / Path(self._pkg_file_name + ".product")).rename(self._pkg_build_directory.parent / self._pkg_file_name)

        return self._sign_pkg()


    def build(self) -> bool:
        """
        Build the application package.
        """

        if all([self._pkg_file_structure is None, self._pkg_preinstall_script is None, self._pkg_postinstall_script is None]):
            raise Exception("Cannot build a package!")

        if Path(self._pkg_output).exists():
            logging.info(f"Removing existing package: {self._pkg_output}")
            Path(self._pkg_output).unlink()

        self._prepare_scripts()
        self._prepare_file_structure()
        if self._build_pkg() is False:
            logging.info("Package build failed.")
            return False
        if self._sign_pkg() is False:
            logging.info("Package signing failed.")
            return False
        if self._convert_to_product_archive() is False:
            logging.info("Package conversion failed.")
            return False

        if not Path(self._pkg_output).parent.exists():
            Path(self._pkg_output).mkdir(parents=True, exist_ok=True)

        subprocess.run(["cp", self._pkg_build_directory.parent / self._pkg_file_name, self._pkg_output])
        logging.info(f"Package built: {self._pkg_output}")
        return True


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(filename)-22s] [%(levelname)-8s] [%(lineno)-3d]: %(message)s",
        handlers=[logging.StreamHandler()]
    )

    test_suites = [
        Packages(
            pkg_output="Sample-Install.pkg",
            pkg_bundle_id="com.myapp.installer",
            pkg_file_structure={
                "Samples/MyApp/MyApp.app": "/Applications/MyApp.app",
                "Samples/MyApp/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
            },
            pkg_preinstall_script="Samples/MyApp/MyPreinstall.sh",
            pkg_postinstall_script="Samples/MyApp/MyPostinstall.sh",
            pkg_as_distribution=True,
        ),
        Packages(
            pkg_output="Sample-Uninstall.pkg",
            pkg_bundle_id="com.myapp.uninstaller",
            pkg_preinstall_script="Samples/MyUninstaller/MyPreinstall.sh",
        ),
        Packages(
            pkg_output="Sample-Wallpaper.pkg",
            pkg_bundle_id="com.myapp.wallpaper",
            pkg_file_structure={
                "Samples/MyWallpaperConfigurator/Snow Leopard Server.jpg": "/Library/Desktop Pictures/Snow Leopard Server.jpg",
            },
            pkg_preinstall_script="Samples/MyWallpaperConfigurator/PrepareDirectory.sh",
            pkg_postinstall_script="Samples/MyWallpaperConfigurator/SetWallpaper.sh",
            pkg_script_resources=[
                "Samples/MyWallpaperConfigurator/desktoppr",
            ],
        ),
    ]

    for test_suite in test_suites:
        if test_suite.build() is False:
            logging.info("Package build failed.")
            exit(1)
