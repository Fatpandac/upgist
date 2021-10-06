"""
FileName: setup.py
Author: Fatpandac
Create: 2021/10/07
Description: Setup upgist.
"""

from setuptools import setup, find_packages

setup(name='upgist',
      version='0.0.2',
      description='Upgist is a gist cli tool.',
      author='Fatpandac',
      author_email='tingfeizheng@gmail.com',
      license='MIT',
      py_modules=['upgist'],
      packages=find_packages(),
      entry_points = """
        [console_scripts]
        upgist = upgist:main
      """
      )
