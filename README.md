# macOS-Pkg-Builder

Python module for creating macOS packages more easily through native tooling (pkgbuild).


## Usage

```py
import macos_pkg_builder

pkg_obj = Packages(
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

pkg_obj.build()
```