"""
__init__.py: Entry point for the macOS-Pkg-Builder library.

Library usage:
    >>> from macos_pkg_builder import Packages

    >>> pkg_obj = macos_pkg_builder.Packages(
    >>>     pkg_output="Sample.pkg",
    >>>     pkg_bundle_id="com.myapp.installer",
    >>>     pkg_preinstall_script="Samples/MyApp/MyPreinstall.sh",
    >>>     pkg_postinstall_script="Samples/MyApp/MyPostinstall.sh",
    >>>     pkg_file_structure={
    >>>         "Samples/MyApp/MyApp.app": "/Applications/MyApp.app",
    >>>         "Samples/MyApp/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
    >>>     },
    >>> )

    >>> assert pkg_obj.build() is True
"""

__title__:        str = "macos_pkg_builder"
__version__:      str = "2.0.1"
__description__:  str = "macOS Package Builder Library, wrapping Apple's 'pkgbuild' and 'productbuild' utilities."
__url__:          str = "https://github.com/ripeda/macOS-Pkg-Builder"
__author__:       str = "RIPEDA Consulting"
__author_email__: str = "info@ripeda.com"
__status__:       str = "Production/Stable"
__all__:         list = ["Packages"]


from .core import DistributionPackage, FlatPackage, Packages