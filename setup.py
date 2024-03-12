from setuptools import setup, find_packages


def read_requirements():
    try:
        with open('requirements.txt') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


setup(
    name='mancaveman',
    version='0.2.0',
    author='Omur Ozbahceliler',
    packages=find_packages(exclude=('tests*', 'docs')),
    install_requires=read_requirements(),
    python_requires='==3.10.*',
    description='Mancave manager',
    url='https://github.com/rootifera/mancaveman-postgresql',
)
