"""
flat_pkg.py: Builds a flat package.
"""

import logging
import plistlib
import tempfile
import subprocess

from pathlib import Path

from .utilities.signing import SignPackage
from .utilities.subprocess_wrapper import SubprocessWrapper, SubprocessErrorLogging


PKGBUILD: str = "/usr/bin/pkgbuild"
CHMOD:    str = "/bin/chmod"
CP:       str = "/bin/cp"
RM:       str = "/bin/rm"


class FlatPackage:

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
                ) -> None:

        self._pkg_output = pkg_output
        self._pkg_bundle_id = pkg_bundle_id
        self._pkg_version = pkg_version
        self._pkg_install_location = pkg_install_location
        self._pkg_allow_relocation = pkg_allow_relocation
        self._pkg_file_structure = pkg_file_structure
        self._pkg_preinstall_script = pkg_preinstall_script
        self._pkg_preflight_script = pkg_preflight_script
        self._pkg_postinstall_script = pkg_postinstall_script
        self._pkg_postflight_script = pkg_postflight_script
        self._pkg_script_resources = pkg_script_resources
        self._pkg_signing_identity = pkg_signing_identity

        self._pkg_temp_directory      = tempfile.TemporaryDirectory()
        self._pkg_temp_directory      = Path(self._pkg_temp_directory.name)
        self._pkg_build_directory     = Path(self._pkg_temp_directory, "build")
        self._pkg_scripts_directory   = Path(self._pkg_temp_directory, "scripts")
        self._pkg_output_directory    = Path(self._pkg_temp_directory, "output")
        self._pkg_resources_directory = Path(self._pkg_temp_directory, "resources")
        self._pkg_temp_output         = Path(self._pkg_temp_directory, Path(self._pkg_output).name)



    def _prepare_scripts(self) -> None:
        """
        Adjusts naming and permissions of scripts to match pkgbuild requirements.
        """

        _working_directory = self._pkg_scripts_directory
        _file_map = {
            "preinstall":  self._pkg_preinstall_script,
            "preflight":   self._pkg_preflight_script,
            "postinstall": self._pkg_postinstall_script,
            "postflight":  self._pkg_postflight_script,
        }

        for script, path in _file_map.items():
            if path is None:
                continue

            if not Path(path).exists():
                raise FileNotFoundError(f"{script.capitalize()} script not found: {path}")

            if not _working_directory.exists():
                _working_directory.mkdir(parents=True, exist_ok=True)

            if Path(_working_directory.joinpath(script)).exists():
                raise FileExistsError(f"Script already exists: {script}")

            SubprocessWrapper([CP, "-c", path, _working_directory.joinpath(script)], raise_on_error=True).run()
            SubprocessWrapper([CHMOD, "+x", _working_directory.joinpath(script)], raise_on_error=True).run()

        if self._pkg_script_resources is not None:
            for resources in self._pkg_script_resources:
                if not Path(resources).exists():
                    raise FileNotFoundError(f"Script resource not found: {resources}")

                if not _working_directory.exists():
                    _working_directory.mkdir(parents=True, exist_ok=True)

                if Path(_working_directory.joinpath(Path(resources).name)).exists():
                    raise FileExistsError(f"Script resource already exists: {resources}")

                SubprocessWrapper([CP, "-c", resources, _working_directory], raise_on_error=True).run()
                SubprocessWrapper([CHMOD, "+x", _working_directory.joinpath(Path(resources).name)], raise_on_error=True).run()


    def _prepare_file_structure(self) -> None:
        """
        Adjusts file structure to match pkgbuild requirements.
        """

        if self._pkg_file_structure is None:
            return

        for source, destination in self._pkg_file_structure.items():
            if not Path(source).exists():
                raise FileNotFoundError(f"Source file does not exist: {source}")

            internal_destination = Path(f"{self._pkg_build_directory}{destination}")

            if not internal_destination.parent.exists():
                internal_destination.parent.mkdir(parents=True, exist_ok=True)

            SubprocessWrapper([CP, "-cR", source, internal_destination], raise_on_error=True).run()


    def _generate_component_file(self) -> Path:
        """
        Generate a component file to prevent the relocation of the embedded application(s).
        """

        # Find anything with an Info.plist embedded, needs to be a valid bundle for pkgbuild.
        bundle = None
        for source, destination in self._pkg_file_structure.items():
            if Path(source, "Contents", "Info.plist").exists():
                bundle = destination
                break

        if bundle is None:
            raise ValueError("No valid bundle found in the provided file structure.")

        contents = [{
            "BundleHasStrictIdentifier": True,
            "BundleIsRelocatable":       self._pkg_allow_relocation,
            "BundleIsVersionChecked":    True,
            "BundleOverwriteAction":     "upgrade",
            "RootRelativeBundlePath":    bundle,
        }]
        file = tempfile.NamedTemporaryFile(delete=False)
        plistlib.dump(contents, file.name.open("wb"))

        return Path(file.name)


    def _generate_pkg_arguments(self) -> list:
        """
        Generate pkgbuild arguments according to the provided configuration.
        """

        args = [
            PKGBUILD,
            "--identifier", self._pkg_bundle_id,
            "--version",    self._pkg_version,
            "--root",       self._pkg_build_directory
        ]

        if self._pkg_scripts_directory.exists():
            args.extend(["--scripts", self._pkg_scripts_directory])

        if self._pkg_file_structure is not None:
            args.extend(["--install-location", self._pkg_install_location])
            if self._pkg_allow_relocation is False:
                args.extend(["--component-plist", self._generate_component_file()])
        else:
            args.extend(["--nopayload"])


        args.extend([self._pkg_temp_output])

        return args


    def _build_pkg(self) -> bool:
        """
        Build a flat package. Private method.
        """
        result = subprocess.run(self._generate_pkg_arguments(), capture_output=True)
        if result.returncode != 0:
            SubprocessErrorLogging(result).log()
            return False

        return True


    def build(self) -> bool:
        """
        Build a flat package. Public method.
        """
        if all([self._pkg_file_structure is None, self._pkg_preinstall_script is None, self._pkg_postinstall_script is None]):
            raise ValueError("Cannot build a package! No file structure or scripts provided.")

        if Path(self._pkg_output).exists():
            # Use over Path.unlink() to avoid weird permission issues.
            SubprocessWrapper([RM, self._pkg_output], raise_on_error=True).run()

        self._pkg_build_directory.mkdir(parents=True, exist_ok=True)

        self._prepare_scripts()
        self._prepare_file_structure()

        if self._build_pkg() is False:
            logging.info("Package build failed.")
            return False

        if self._pkg_signing_identity is not None:
            if SignPackage(self._pkg_temp_output, self._pkg_signing_identity).sign() is False:
                return False

        SubprocessWrapper([CP, "-c", self._pkg_temp_output, self._pkg_output], raise_on_error=True).run()

        logging.info(f"Flat Package built: {self._pkg_output}")

        return True
