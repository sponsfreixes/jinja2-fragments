from setuptools import find_packages, setup

requires = [
    "jinja2",
]

tests_requires = [
    "pytest",
]

dev_requires = [
    "pre-commit",
]

setup(
    name="jinja2_fragments",
    version="1.0.0",
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
)
