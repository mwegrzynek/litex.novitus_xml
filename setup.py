from os import path
from setuptools import setup


version = '1.0.0'


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='litex.novitus_xml',
    version=version,
    description='A Novitus XML Protocol Fiscal Printer Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Michał Węgrzynek',
    author_email='mwegrzynek@litexservice.pl',
    namespace_packages=['litex'],
    packages=[
        'litex.novitus_xml'
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyserial',
        'lxml'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries'
    ],
)
