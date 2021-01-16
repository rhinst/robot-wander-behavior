from setuptools import setup, find_packages
import platform


setup(
  name='robot-wander-behavior',
  version='0.1',
  description='Robot wander behavior',
  url='https://github.com/rhinst/robot-wander-behavior',
  author='Rob Hinst',
  author_email='rob@hinst.net',
  license='MIT',
  packages=find_packages(),
  data_files = [
    ('config', ['config/default.yaml']),
    ('config/dev', ['config/dev/env.yaml.dist']),
  ],
  install_requires = [
    'redis==3.5.3',
    'himl==0.7.0',
  ],
  test_suite='tests',
  tests_require=['pytest==6.2.1'],
  entry_points={
    'console_scripts': ['wander=app.__main__:main']
  }
)