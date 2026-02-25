from setuptools import find_packages, setup

package_name = 'autonomus_takeoff_landing'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shubham',
    maintainer_email='shubhamjolapara256@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gps_monitor = autonomus_takeoff_landing.gps_monitor:main',
            'gps_disabler = autonomus_takeoff_landing.gps_disabler:main',
        ],
    },
)
