from setuptools import setup, find_packages


setup(
    name='inventario',
    version='0.0.1',
    description='inventario',
    author='Javier Santacruz',
    author_email='javier.santacruz.lc@gmail.com',
    url='https://github.com/jvrsantacruz/inventario',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'xlrd',
        'click',
        'Flask'
    ],
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    platforms=['Unix'],
    entry_points={
        'console_scripts': ['inv = inventario.cli:main']
    }
)
