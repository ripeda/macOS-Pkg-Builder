# macOS Pkg Builder

## 1.0.9
- CI: Switch to `svenstaro/upload-release-action@v2`
- Resolve Munki erroring on payload-less packages
  - Enforces `--root` parameter for `pkgbuild`
- Add support for pre/postflight scripts
  - Configured via new `pkg_preflight_script` and `pkg_postflight_script` parameters
- Enforce stricter bin pathing for `cp` and `chmod`
  - Avoids 3rd party tools from being used

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