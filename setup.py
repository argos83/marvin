from setuptools import setup, find_packages

setup(name='marvin',
      version='0.1.0',
      description='Marvin - Automation Framework',
      url='https://github.com/argos83/marvin',
      author='Sebastian Tello',
      author_email='argos83@gmail.com',
      packages=find_packages(exclude=("tests", "examples")),
      include_package_data=True,
      install_requires=['colorama'],
      tests_require=['pytest', 'pytest-cov', 'flake8'],
      zip_safe=False)
