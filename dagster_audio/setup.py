from setuptools import find_packages, setup

setup(
    name="dagster_audio",
    packages=find_packages(exclude=["dagster_audio_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
