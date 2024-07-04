from pathlib import Path

from setuptools import find_packages, setup

requires = [
    "jinja2 >= 3.1.0",
]

tests_requires = [
    "quart >= 0.18.0",
    "flask >= 2.1.0",
    "fastapi",
    "sanic",
    "sanic_ext",
    "sanic_testing",
    "starlette[full]",
    "pytest",
    "pytest_asyncio",
    "litestar[standard]",
]

dev_requires = [
    "pre-commit",
]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="jinja2_fragments",
    version="1.4.1",
    description="Render Jinja2 template block as HTML page fragments on Python "
    "web frameworks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sergi Pons Freixes",
    author_email="sergi@cub3.net",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"jinja2_fragments": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    extras_require={"dev": dev_requires, "tests": tests_requires},
    install_requires=requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    url="https://github.com/sponsfreixes/jinja2-fragments",
    project_urls={
        "Source Code": "https://github.com/sponsfreixes/jinja2-fragments",
        "Issue Tracker": "https://github.com/sponsfreixes/jinja2-fragments/issues",
        "Changes": "https://github.com/sponsfreixes/jinja2-fragments/blob/main/CHANGELOG.md",  # noqa
    },
)
