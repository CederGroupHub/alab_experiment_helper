from pathlib import Path

from setuptools import setup, find_packages

setup(
    name="alab_experiment_helper",
    packages=find_packages(exclude=["tests", "tests.*"]),
    version="0.0.1",
    author="Alab Project Team",
    python_requires=">=3.6",
    description="Helper package for generate input files for alab_management software",
    zip_safe=False,
    install_requires=[
        package.strip("\n")
        for package in (Path(__file__).parent / "requirements.txt").open("r", encoding="utf-8").readlines()],
    include_package_data=True,
)
