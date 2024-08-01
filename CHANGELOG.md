# macOS Pkg Builder

## 2.3.0
- Fix missing `FlatPackage` and `DistributionPackage` class declaration in `__all__` attribute

## 2.2.0
- Perform volume verification on whether Copy on Write (COW) is available
  - Resolves crashing on HFS+ volumes.
- Add automatic detection of source file copying
  - Resolves crashing when directories are passed to `pkg_script_resources`
- Set BSD 3-Clause License

## 2.0.2
- Resolve `open` error on component file generation

## 2.0.1
- Resolve packages embedding an empty pkg at `/`
  - Regression from 2.0.0

## 2.0.0
- Implement new `FlatPackage` and `DistributionPackage` classes
  - Intended for more advanced package configurations, including bundling multiple PKGs inside a single distribution package
- Implement more robust subprocess logging for errors
- Implement Copy on Write (COW) for package resources
  - 20% faster package creation on average

## 1.2.0
- Expand distribution type package configuration:
  - Pass MARKDOWN to configure welcome, readme and licensing in the package
  - Pass light and dark mode images to configure the package background
  - Pass title to configure the package title
    - Header: `Install {title}`
    - Welcome: `Welcome to the {title} Installer`
- Add additional FileNotFound error handling for missing resources
- Add support for passing README and LICENSE content to the package as markdown
  - Configured via new `pkg_readme` and `pkg_license` parameters

## 1.1.1
- Fix project name typo in `setup.py`

## 1.1.0
- CI: Switch to `svenstaro/upload-release-action@v2`
- Resolve Munki erroring on payload-less packages
  - Enforces `--root` parameter for `pkgbuild`
- Add support for pre/postflight scripts
  - Configured via new `pkg_preflight_script` and `pkg_postflight_script` parameters
- Enforce stricter bin pathing for `cp` and `chmod`
  - Avoids 3rd party tools from being used
- Publish project version via `__version__` attribute
- Convert project to a package

## 1.0.8
- Add support for signing distribution archive
- Resolve missing return statement in `_sign_pkg()`

## 1.0.7
- Add support for distributing as product archive.
  - Generated with `productbuild`
  - Configured via new `pkg_as_distribution` parameter

## 1.0.6
- Switch to logging module for printing
  - To be configured by the calling script

## 1.0.5
- Fix signing issue with `pkg_signing_identity` parameter

## 1.0.4
- Add support for pkg signing
  - Configured via new `pkg_signing_identity` parameter

## 1.0.3
- Add support for bundling additional resources for pre/postinstall scripts to access
  - Files to be defined via new `pkg_script_resources` parameter
  - Current working directory for scripts will be the same directory containing additional resources

## 1.0.2
- Create output directory if it doesn't exist

## 1.0.1
- Resolve import errors from PyPi

## 1.0.0
- Initial release