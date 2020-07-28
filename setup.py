from setuptools import setup, find_packages


setup(
    name="algotradingstuff",
    version="0.0.1",
    author="dcl10_pypi",
    description="A small example package",
    long_description_content_type="text/markdown",
    url="https://github.com/dcl10/AlgoTradingStuff",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=['requests'],
    test_suite='tests',
    python_requires='>=3.7',
    license='MIT'
)
