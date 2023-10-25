from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in auto_commission/__init__.py
from auto_commission import __version__ as version

setup(
	name="auto_commission",
	version=version,
	description="Auto Commission Journal Entry ",
	author="Bantoo",
	author_email="devs@thebantoo.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
