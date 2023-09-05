# macOS-Pkg-Builder

Python module for creating macOS packages more easily through native tooling (pkgbuild). Primarily developed as an alternative to [WhiteBox's Packages](http://s.sudre.free.fr/Software/Packages/about.html) for easier CI/CD integration.

* [GitHub](https://github.com/ripeda/macOS-Pkg-Builder)
* [PyPi](https://pypi.org/project/macos-pkg-builder)

## Usage

Installation:
```
pip3 install macos-pkg-builder
```

Sample invocation:
```py
import macos_pkg_builder

pkg_obj = macos_pkg_builder.Packages(
    pkg_output="Sample.pkg",
    pkg_bundle_id="com.myapp.installer",
    pkg_preinstall_script="Samples/MyApp/MyPreinstall.sh",
    pkg_postinstall_script="Samples/MyApp/MyPostinstall.sh",
    pkg_file_structure={
        "Samples/MyApp/MyApp.app": "/Applications/MyApp.app",
        "Samples/MyApp/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",
    },
)

pkg_obj.build()
```


Format of `Packages` constructor:
```py
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

    File Structure:
        {
            # Source: Destination
            "~/Developer/MyApp.app": "/Applications/MyApp.app",
            "~/Developer/MyLaunchDaemon.plist": "/Library/LaunchDaemons/com.myapp.plist",

        }
"""
```

## Additional Supported Use Cases

#### Building single-use packages that don't leave tooling behind

Useful for scenarios where you need to ship additional tools, but don't want to run any additional cleanup scripts to remove them.

Below is how to set a wallpaper using Scripting OS X's [desktoppr](https://github.com/scriptingosx/desktoppr):

```py
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
```

#### Building a simple uninstaller

Useful for when you have a single script you need to execute to remove your application:
```py
Packages(
    pkg_output="Sample-Uninstall.pkg",
    pkg_bundle_id="com.myapp.uninstaller",
    pkg_preinstall_script="Samples/MyUninstaller/MyPreinstall.sh",
),
```