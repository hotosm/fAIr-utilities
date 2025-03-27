from setuptools import setup, find_packages
import os

if os.path.exists('./ramp-code'):
    pass
else:
    print('[WARNING] - ramp-code folder does not exist, some functionalities may not work correctly.')

setup(
    package_dir={"": "."},
    packages=find_packages(include=["hot_fair_utilities", "hot_fair_utilities.*"]),
    include_package_data=True,
)
