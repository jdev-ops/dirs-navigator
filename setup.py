import setuptools
import pathlib

from setuptools import find_packages

here = pathlib.Path(__file__).parent.resolve()

install_requires = (
    (here / "requirements/common.txt").read_text(encoding="utf-8").splitlines()
)


setuptools.setup(
    name="dev-navigator",
    version="0.0.1",
    author="J. Albert Cruz",
    author_email="jalbertcruz@gmail.com",
    license="MIT",
    package_dir={
        "": "lib",
    },
    packages=find_packages("lib"),
    install_requires=install_requires,
    include_package_data=True,
    scripts=[
        # "bin/ch-d",
    ],
    entry_points={
        "console_scripts": [
            "sel-env=dir_nav.navigator:sel_env",
            "_choose-destination=dir_nav.navigator:choose_destination",
        ],
    },
)
