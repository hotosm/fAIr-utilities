from setuptools import setup, find_packages
import os

if os.path.exists('./ramp-code'):
    print('ramp-code exists, starting setup')
else:
    print('ramp-code not found, cloning from github')
    os.system('git clone https://github.com/kshitijrajsharma/ramp-code-fAIr.git ./ramp-code')

setup(
    package_dir={"": "."},
    packages=find_packages(include=["hot_fair_utilities", "hot_fair_utilities.*", "ramp", "ramp.*"]),
    include_package_data=True,
)
