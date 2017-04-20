from setuptools import setup


setup(
    name='usolitaire',
    version='0.0.1',
    packages=('usolitaire',),
    entry_points={
        'console_scripts': {
            'usolitaire = usolitaire.app:main',
        }
    },
)
