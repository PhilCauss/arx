from setuptools import setup, find_packages

# ... your existing imports/description remain the same ...

setup(
    name="arx",
    version="1.0.1",
    author="Arx Developer",
    description="A secure wrapper around yay package manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PhilCauss/arx",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        # ... same classifiers ...
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "arx=arx.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
