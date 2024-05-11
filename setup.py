from setuptools import setup, find_packages


setup(
    name='hhvs',
    version='0.0.1',
    packages=find_packages(),
    install_requires=open('requirements.txt').read(),
)
