import re
from setuptools import setup, find_packages


with open('marvin/version.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)


setup(name='marvin-test',
      version=version,
      description='Marvin - Automation Framework',
      url='https://github.com/argos83/marvin',
      author='Sebastian Tello',
      author_email='argos83@gmail.com',
      packages=find_packages(exclude=("tests", "examples")),
      include_package_data=True,
      install_requires=['colorama', 'pyyaml'],
      tests_require=['pytest', 'pytest-cov', 'flake8', 'freezegun'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'marvin=marvin.runner.cli:main'
          ]
      },
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'
      ]
)
