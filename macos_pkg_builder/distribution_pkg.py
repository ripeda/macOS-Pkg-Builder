"""
distribution_pkg.py: Builds a distribution package.
"""

import logging
import markdown
import tempfile
import subprocess

from pathlib import Path
from xml.etree import ElementTree as ET

from .utilities.signing import SignPackage
from .utilities.subprocess_wrapper import SubprocessWrapper, SubprocessErrorLogging


PRODUCTBUILD: str = "/usr/bin/productbuild"
CP:           str = "/bin/cp"


class DistributionPackage:

    def __init__(self,
                 pkg_inputs:              list[str],
                 pkg_output:              str,
                 pkg_bundle_id:           str = None,
                 pkg_version:             str = None,
                 pkg_signing_identity:    str = None,
                 pkg_title:               str = None,
                 pkg_welcome:             str = None,
                 pkg_readme:              str = None,
                 pkg_license:             str = None,
                 pkg_background:          str = None,
                 pkg_background_dark:     str = None,
                 ) -> None:

        self._pkg_inputs = pkg_inputs
        self._pkg_output = pkg_output
        self._pkg_bundle_id = pkg_bundle_id
        self._pkg_version = pkg_version
        self._pkg_signing_identity = pkg_signing_identity
        self._pkg_title = pkg_title
        self._pkg_welcome = pkg_welcome
        self._pkg_readme = pkg_readme
        self._pkg_license = pkg_license
        self._pkg_background = pkg_background
        self._pkg_background_dark = pkg_background_dark

        self._markdown_file_mapping = {
            self._pkg_welcome: "WELCOME.html",
            self._pkg_readme:  "README.html",
            self._pkg_license: "LICENSE.html"
        }

        # If a dark background is not provided, use the light background.
        if self._pkg_background is not None and self._pkg_background_dark is None:
            self._pkg_background_dark = self._pkg_background

        self._background_mapping = {
            "light": {
                "property": self._pkg_background,
                "file": f"BACKGROUND{Path(self._pkg_background).suffix if self._pkg_background is not None else ''}",
                "label": "background",
            },
            "dark": {
                "property": self._pkg_background_dark,
                "file": f"BACKGROUND-DARK{Path(self._pkg_background_dark).suffix if self._pkg_background_dark is not None else ''}",
                "label": "background-darkAqua",
            }
        }
        self._pkg_temp_directory      = tempfile.TemporaryDirectory()
        self._pkg_temp_directory      = Path(self._pkg_temp_directory.name)
        self._pkg_resources_directory = Path(self._pkg_temp_directory, "resources")


    def _prepare_markdown_resources(self) -> None:
        """
        Convert content from markdown to HTML, then save it to the resources directory.
        """
        for file in self._markdown_file_mapping:
            if file is None:
                continue

            Path(self._pkg_resources_directory).mkdir(parents=True, exist_ok=True)

            with open(self._pkg_resources_directory / self._markdown_file_mapping[file], "w") as f:
                f.write("<!DOCTYPE html>\n<html>\n<head>\n<style>\nbody { font-family: -apple-system; }\n</style>\n</head>\n<body>\n")
                f.write(markdown.markdown(file))
                f.write("</body>\n</html>\n")


    def _prepare_background_resources(self) -> None:
        """
        Prepare background resources for the distribution package.
        """
        # Check if light and dark are the same, if so, only copy one.
        if self._background_mapping["light"]["property"] == self._background_mapping["dark"]["property"]:
            self._background_mapping["dark"]["property"] = None
            self._background_mapping["dark"]["file"] = self._background_mapping["light"]["file"]

        for background in self._background_mapping:
            if self._background_mapping[background]["property"] is None:
                continue
            if not Path(self._background_mapping[background]["property"]).exists():
                raise FileNotFoundError(f"Background image not found: {self._background_mapping[background]['property']}")

            Path(self._pkg_resources_directory).mkdir(parents=True, exist_ok=True)
            SubprocessWrapper([CP, "-c", self._background_mapping[background]["property"], self._pkg_resources_directory.joinpath(self._background_mapping[background]["file"])], raise_on_error=True).run()


    def _prepare_distribution_file(self, input_file: tempfile.NamedTemporaryFile) -> None:
        """
        Sync the distribution file with the provided content.
        """
        tree = ET.parse(input_file.name)
        root = tree.getroot()

        if self._pkg_title is not None:
            element = ET.Element("title")
            element.text = self._pkg_title
            root.append(element)

        for background in self._background_mapping:
            element = ET.Element(self._background_mapping[background]["label"], file=self._background_mapping[background]["file"], alignment="bottomleft", scaling="tofit")
            root.append(element)

        for file in self._markdown_file_mapping:
            if file is not None:
                element_name = self._markdown_file_mapping[file].split(".")[0].lower()
                element = ET.Element(element_name, file=self._markdown_file_mapping[file], mimetype="text/html")
                root.append(element)

        tree.write(input_file.name)


    def _generate_pkg_synthesize_arguments(self, output: str) -> list:
        """
        Generate productbuild synthesize arguments according to the provided configuration.
        """

        args = [
            PRODUCTBUILD,
            "--synthesize",
        ]
        for pkg in self._pkg_inputs:
            args.extend(["--package", pkg])

        if self._pkg_bundle_id is not None:
            args.extend(["--identifier", self._pkg_bundle_id])
        if self._pkg_version is not None:
            args.extend(["--version", self._pkg_version])

        args.extend([output])

        return args


    def _generate_pkg_build_arguments(self, distribution_file: tempfile.NamedTemporaryFile) -> list:
        """
        Generate productbuild arguments according to the provided configuration.
        """

        args = [
            PRODUCTBUILD,
            "--distribution", distribution_file.name,
            "--resources", self._pkg_resources_directory
        ]

        for pkg in self._pkg_inputs:
            args.extend(["--package-path", Path(pkg).parent])

        args.extend([self._pkg_output + ".product"])

        return args


    def build(self) -> bool:
        """
        Build the distribution package.
        """

        distribution_file = tempfile.NamedTemporaryFile(delete=False)

        result = subprocess.run(self._generate_pkg_synthesize_arguments(distribution_file.name), capture_output=True)
        if result.returncode != 0:
            SubprocessErrorLogging(result).log()
            return False

        self._prepare_markdown_resources()
        self._prepare_background_resources()
        self._prepare_distribution_file(distribution_file)

        result = subprocess.run(self._generate_pkg_build_arguments(distribution_file), capture_output=True)
        if result.returncode != 0:
            SubprocessErrorLogging(result).log()
            return False

        if self._pkg_signing_identity is not None:
            SignPackage(self._pkg_output + ".product", self._pkg_signing_identity).sign()

        # Rename output file.
        if Path(self._pkg_output).exists():
            Path(self._pkg_output).unlink()
        Path(self._pkg_output + ".product").rename(self._pkg_output)

        logging.info(f"Distribution package built: {self._pkg_output}")

        return True