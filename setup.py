import os
import pkg_resources
import setuptools

# GET THE README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# GET THE VERSION
HERE = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(HERE, "paec", "__version__.py")) as f:
    exec(f.read(), version)

# REQUIREMENTS
with open("requirements/prod.txt", "r") as file:
    prod_requirements = [str(req) for req in pkg_resources.parse_requirements(file)]

with open("requirements/test.txt", "r") as file:
    test_requirements = [str(req) for req in pkg_resources.parse_requirements(file)]
    # Remove the prod_requirements
    test_requirements = list(set(test_requirements) - set(prod_requirements))


setuptools.setup(
    name="paec",
    version=version["__version__"],
    author="Altas Technologies",
    description="Python Altas Exchange Connectivity",
    install_requires=prod_requirements,
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    extras_require={"test": test_requirements},
)
