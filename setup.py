#!/usr/bin/env python3
# @file setup.py
# @brief Setup file that packages the project for pip.
# @author Justin Gallagher (jrgallag@andrew.cmu.edu)
# @since 2015-11-08

from setuptools import setup

setup(name='cmu-course-api',
      version='1.1.0',
      description=('Python utility for retrieving information about courses at'
                   ' Carnegie Mellon University.'),
      url='http://scottylabs.org/course-api',
      author='ScottyLabs',
      author_email='info@scottylabs.org',
      license='MIT',
      packages=['cmu_course_api'],
      package_data={'cmu_course_api': ['data/*']},
      install_requires=[
        'beautifulsoup4==4.4.1',
        'cmu_auth==0.1.7'
      ],
      scripts=['bin/cmu-course-api'])
