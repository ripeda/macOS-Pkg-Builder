from setuptools import setup, find_packages

def fetch_property(property: str) -> str:
    """
    Fetch a property from macos_pkg_builder.

    Parameters:
        property (str): The name of the property to fetch.

    Returns:
        The value of the property.
    """
    for line in open("macos_pkg_builder/__init__.py", "r").readlines():
        if not line.startswith(property):
            continue
        return line.split("=")[1].strip().strip('"')
    raise ValueError(f"Property {property} not found.")


def resolve_markdown_assets(file: str) -> str:
    """
    README may reference local resources that PyPI does not have access to.
    Thus resolve local resources to their remote counterparts.

    Currently only the following resources are referenced in the README:
    - Markdown-Welcome.png

    Returns:
        The resolved README contents.
    """
    repo_base = fetch_property("__url__:")
    repo_raw = repo_base.replace("github.com", "raw.githubusercontent.com")

    contents = open(file, "r").read()
    contents = contents.replace("src=\"Samples/Demos/Markdown-Welcome.png\"", f"src=\"{repo_raw}/main/Samples/Demos/Markdown-Welcome.png\"")

    return contents


setup(
    name='macos_pkg_builder',
    version=fetch_property("__version__:"),
    description=fetch_property("__description__:"),
    author=fetch_property("__author__:"),
    author_email=fetch_property("__author_email__:"),
    url=fetch_property("__url__:"),
    long_description=resolve_markdown_assets("README.md"),
    long_description_content_type='text/markdown',
    license='',
    python_requires='>=3.6',
    packages=find_packages(include=["macos_pkg_builder", "macos_pkg_builder.utilities"]),
    package_data={
        "macos_pkg_builder": [
            "__init__.py",
            "core.py",
            "distribution_pkg.py",
            "flat_pkg.py",
        ],
        "macos_pkg_builder.utilities": [
            "__init__.py",
            "signing.py",
            "subprocess_wrapper.py",
        ],
    },
    py_modules=["macos_pkg_builder"],
    install_requires=open("requirements.txt", "r").readlines(),
)