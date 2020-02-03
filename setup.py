from setuptools import setup, find_packages

setup(
    name="actimanager-external",
    description="ACTiManager External",
    author="ACTiCLOUD",
    author_email="simonkollberg@gmail.com",
    url="https://acticloud.eu",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "colorama",
        "heat-spreader",
        "aio-pika>=6.4.1,<7.0.0",
        "structlog>=19.1.0,<20.0.0",
        "openstacksdk>=0.31.1",
    ],
    entry_points={
        "console_scripts": [
            "actimanager-external = actimanager_external.__main__:main"
        ]
    },
)
