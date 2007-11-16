from setuptools import setup, find_packages

version = '1.0rc1'

setup(name='bicop',
      version=version,
      description="Read bind-style configuration files",
      long_description=open("README.txt").read(),
      classifiers=[
          "Development Status :: 6 - Mature",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='configparser configuration parser ISC bind',
      author='Wichert Akkerman - Simplon',
      author_email='wichert@simplon.biz',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      tests_require="nose>=0.10.0b1",
      test_suite="nose.collector",
      )
