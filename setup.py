from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='mancaveman',
    version='1.0.0',
    author='Omur Ozbahceliler',
    packages=find_packages(),
    install_requires=requirements,
)
