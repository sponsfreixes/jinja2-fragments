from setuptools import find_packages, setup

requires = [
    "jinja2 >= 3.1.0",
]

tests_requires = [
    "pytest",
    "flask >= 2.1.0",
]

dev_requires = [
    "pre-commit",
]

setup(
    name="jinja2_fragments",
    version="0.1.0",
    description="Render Jinja2 template block as HTML page fragments on Python "
    "web frameworks.",
    author="Sergi Pons Freixes",
    author_email="sergi@cub3.net",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    extras_require={"dev": dev_requires, "tests": tests_requires},
    install_requires=requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
