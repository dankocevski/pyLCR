from setuptools import setup

setup(
    name='pyLCR',
    version='0.1.0',    
    description='A Python package to access the Fermi LAT LCR',
    url='https://github.com/dankocevski/LCR',
    author='Daniel Kocevski',
    author_email='daniel.kocevski@nasa.gov',
    license='BSD 2-clause',
    packages=['pyLCR'],
    install_requires=['numpy',                     
                      ],

    classifiers=[
        'Programming Language :: Python :: 3.10.2',
    ],
)
