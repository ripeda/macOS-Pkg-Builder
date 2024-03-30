"""
validation.py: Validates project
"""
import logging

from macos_pkg_builder import Packages


def main():
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

if __name__ == "__main__":
    main()