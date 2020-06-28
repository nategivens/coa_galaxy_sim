from setuptools import setup, find_packages

setup(
    name='coa_galaxy_sim',
    version='0.1',
    description='A module to aid in world building for the fictional Chronicles of Ascension sci-fi setting',
    url='',
    author='Nathaniel Givens',
    author_email='nathaniel.givens@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    install_requires=['numpy', 'PyYAML', 'pandas']
)