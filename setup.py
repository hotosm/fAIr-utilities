# Third party imports
from setuptools import find_packages, setup

setup(
    package_dir={"": "."},
    packages=find_packages(include=["hot_fair_utilities", "hot_fair_utilities.*"]),
    include_package_data=True,
)
