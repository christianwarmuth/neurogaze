from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split('\n')

setup(
    author='Philipp Bode, Christian Warmuth',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description=(
        'neurogaze provides wrapper functionality to record and '
        'visualize eye tracking and application usage data.'
    ),
    install_requires=requirements,
    license='MIT license',
    long_description=readme,
    include_package_data=True,
    name='neurogaze',
    packages=find_packages(include=['neurogaze']),
    url='https://github.com/christianwarmuth/neurogaze',
    version='0.0.1',
)
