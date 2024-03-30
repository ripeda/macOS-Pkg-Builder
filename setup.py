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

setup(
    name='macos_pkg_builder',
    version=fetch_property("__version__:"),
    description=fetch_property("__description__:"),
    author=fetch_property("__author__:"),
    author_email=fetch_property("__author_email__:"),
    url=fetch_property("__url__:"),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='',
    python_requires='>=3.6',
    packages=find_packages(include=["macos_pkg_builder"]),
    package_data={
        "macos_pkg_builder": [
            "__init__.py",
            "core.py"
        ],
    },
    py_modules=["macos_pkg_builder"],
)