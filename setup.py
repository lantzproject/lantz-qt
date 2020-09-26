from setuptools import setup
import codecs


def read(filename):
    return codecs.open(filename, encoding='utf-8').read()


long_description = '\n\n'.join([read('README'),
                                read('AUTHORS'),
                                read('CHANGES')])

setup(
    name='lantz-qt',
    version='0.6.0',
    license='BSD 3-Clause License',
    description='Qt Library for Lantz',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lantzproject/lantz-qt',
    author='Hernan E. Grecco',
    author_email='hernan.grecco@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    keywords='lantz, lantz-qt, qt, hardware interface, instrumentation framework, science, research',
    packages=[
        'lantz.qt',
        'lantz.qt.blocks',
        'lantz.qt.utils',
        'lantz.qt.widgets',
    ],
    zip_safe=False,
    python_requires='>=3.6, <4',
    install_requires=[
        'pyqt5>=5.15.1',
        'lantzdev>=0.6',
    ],
    entry_points={
        'console_scripts': [
            'lantz-qtdemo = lantz.qt.__main__:main',
        ],
        'lantz_subcommands': [
            'qtdemo = lantz.qt.__main__:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/lantzproject/lantz-qt/issues',
        'Source': 'https://github.com/lantzproject/lantz-qt/',
    },
    include_package_data=True,
    options={'bdist_wheel': {'universal': '1'}},
)
