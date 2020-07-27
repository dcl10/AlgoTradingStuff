from setuptools import setup, find_packages


setup(
    name="algotradingstuff",
    version="0.0.1",
    author="Daniel Lea",
    description="A small example package",
    long_description_content_type="text/markdown",
    url="https://github.com/dcl10/AlgoTradingStuff",
    packages=find_packages(),
    install_requires=['requests'],
    test_suite='tests',
    tests_require=['pytest'],
    python_requires='>=3.7',
    license='MIT'
)
