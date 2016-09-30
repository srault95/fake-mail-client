# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages
from fake_mail_client import version

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_readme():
    readme_path = os.path.abspath(os.path.join(CURRENT_DIR, 'README.rst'))
    if os.path.exists(readme_path):
        with open(readme_path) as fp:
            return fp.read()
    return ""

setup(
    name='fake-mail-client',
    version=version.version_str(),
    url='https://github.com/srault95/fake-mail-client', 
    description='Mail Tools for SMTP load testing',
    long_description=get_readme(),
    author='Stéphane RAULT',
    license='BSD',
    author_email='stephane.rault@radicalspam.org',
    keywords=['testing', 'mail', 'smtp'],
    classifiers=[
        'Topic :: Communications :: Email',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators'
    ],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'fake-factory',
        'arrow',
        'click',
        'PyYAML',
        'tablib'
    ],
    extras_require = {
        'gevent': ['gevent>=1.0'],
    },
    entry_points={
      'console_scripts': [
        'fake-mailer = fake_mail_client.runner:main',
      ],
    },
    test_suite='nose.collector',
)
