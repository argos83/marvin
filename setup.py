from setuptools import setup, find_packages

setup(name='marvin-test',
      version='0.1.0.dev1',
      description='Marvin - Automation Framework',
      url='https://github.com/argos83/marvin',
      author='Sebastian Tello',
      author_email='argos83@gmail.com',
      packages=find_packages(exclude=("tests", "examples")),
      include_package_data=True,
      install_requires=['colorama', 'pyyaml'],
      tests_require=['pytest', 'pytest-cov', 'flake8'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'marvin=marvin.runner.cli:main'
          ]
      })
