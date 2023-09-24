from pathlib import Path
from setuptools import setup

long_description = Path("README.md").read_text()
install_requires = Path("requirements.txt").read_text().splitlines(keepends=False)

setup(
    name="EAplanner",
    description="The code used for RCPSP-VAD optimization using metaheuristics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Hoorn",
    version="0.1",
    url="",
    author_email="a.hoorn@student.vu.nl",
    python_requires=">=3.11",
    install_requires=install_requires,
    packages=[
        "eaplanner",
    ],
)
