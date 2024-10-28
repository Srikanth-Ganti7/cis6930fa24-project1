from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Balasai Srikanth Ganti',
	authour_email='ganti.b@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)