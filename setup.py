from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name="algotradingstuff",
    version="0.0.1",
    author="dcl10_pypi",
    description="A package to interact with the OANDA v20 API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcl10/AlgoTradingStuff",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=['requests'],
    test_suite='tests',
    python_requires='>=3.7',
    license='MIT'
)
