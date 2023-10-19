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
        "bin/setup2",
    ],
    entry_points={
        "console_scripts": [
            # "branch-setup=git_policy.branch_setup:main",
        ],
    },
)
