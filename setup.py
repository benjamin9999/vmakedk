from distutils.core import setup

setup(
    name='vmakedk',
    description='Tools for creating virtual machine images',
    long_description=open('README.txt').read(),
    url='https://github.com/benjamin9999/vmakedk/',
    version='0.2.1',
    author='Benjamin Yates',
    author_email='benjamin@rqdq.com',
    packages=['vmakedk', 'vmakedk.test'],
    scripts=['bin/vmakedk'],
    license='Creative Commons Attribution-ShareAlike 3.0 Unported License',
    install_requires=[],
)
