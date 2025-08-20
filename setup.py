import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'tng_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.py*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Markus Wünstel',
    maintainer_email='markus.wuenstel@tngtech.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "rfm_action_server = tng_control.rfm_action_server:main",
            "rfm_client = tng_control.rfm_client:main",
        ],
    },
)
