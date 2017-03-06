from setuptools import setup, find_packages

setup(name='sparks_pif_converters',
    version='0.0.1',
    url='http://github.com/CitrineInformatics/X-pif-converters',
    description='Parsers to create PIFs from crystal characterization instruments',
    author='Chris Borg',
    author_email='cborg@citrine.io',
    packages=find_packages(),
    install_requires=[
        'pypif',
        'peakutils',
        'pillow',
        'pyxrd'   
    ]
)
