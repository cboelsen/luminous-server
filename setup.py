from setuptools import setup, find_packages


setup(
    name='luminous',
    version='0.0.1',
    author='Christian Boelsen',
    author_email='christianboelsen+github@gmail.com',
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'luminous-server = luminous_project.manage:launch_web_app',
            # 'rusty-updatedb = rusty_neutron.utils.update_db:main',
            # 'rusty-date-media = rusty_neutron.utils.date_photos:main',
            # 'rusty-extract-from-filename = rusty_neutron.utils.extract_data_from_filename:main',
            # 'rusty-extract-from-exif = rusty_neutron.utils.extract_data_from_exif:main',
            # 'rusty-orientation = rusty_neutron.utils.extract_orientation:main',
        ],
    },
    license='LICENSE',
    description='',
    install_requires=[
        'coreapi >= 2.0',
        'django >= 1.10',
        'djangorestframework >= 3.5',
        'django-cors-headers >= 2.0',
        'django-filter >= 1.0.1',
        'gunicorn >= 19.4.5',
        'jpegtran-cffi >= 0.5.2',
        'openapi-codec >= 1.1.7',
        'piexif >= 1.0.3',
        'raven >= 5.11.2',
    ],
)
