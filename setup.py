from setuptools import setup


setup(name='compress',
      version='1.0',
      description='Compression tool using Huffman coding.',
      url='https://github.com/worstof3/compress',
      author='Łukasz Karpiński',
      packages=['compress'],
      test_suite='compress.tests',
      entry_points={
          'console_scripts': ['compress=compress.compress:main'],
      })