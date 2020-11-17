from setuptools import setup

MINOR_VERSION = 0
setup(
    name='filediff',
    version='1.0.{}'.format(MINOR_VERSION),
    package_dir={"kespry": "."},
    packages=['kespry'],
    long_description=open('README.md').read(),
    url='https://github.com/kespry/filediff',
    author_email='fico@kespry.com',
    author='Federico Cesari'
)