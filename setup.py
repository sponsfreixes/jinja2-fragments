from pathlib import Path

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

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="jinja2_fragments",
    version="0.1.0",
    description="Render Jinja2 template block as HTML page fragments on Python "
    "web frameworks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
)
