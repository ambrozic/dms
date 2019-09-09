from setuptools import find_packages, os, setup

with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "dms/__init__.py")
) as f:
    META = {
        x[0]: x[1].strip()[1:-1]
        for x in [l.split(" = ", 1) for l in f.readlines() if not l.find("__")]
    }

with open("readme.md") as f:
    long_description = f.read()

setup(
    name="dms",
    version=META["__version__"],
    author="ambrozic",
    author_email="ambrozic@gmail.com",
    maintainer="ambrozic",
    maintainer_email="ambrozic@gmail.com",
    description="database management service dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/ambrozic/dms",
    project_urls={
        "Code": "https://github.com/ambrozic/dms",
        "Documentation": "https://ambrozic.github.io/dms",
    },
    keywords="database management service dashboard admin",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "databases==0.2.5",
        "itsdangerous==1.1.0",
        "jinja2==2.10.1",
        "passlib==1.7.1",
        "python-multipart==0.0.5",
        "sqlalchemy==1.3.8",
        "starlette==0.12.9",
        "uvicorn==0.8.6",
    ],
    extras_require={
        "postgresql": ["asyncpg==0.18.3", "psycopg2-binary==2.8.3"],
        "sqlite": ["aiosqlite==0.10.0"],
        "docs": [
            "mkdocs-material==4.4.2",
            "mkdocs==1.0.4",
            "pygments==2.4.2",
            "pymdown-extensions==6.0",
        ],
        "tests": [
            "black==19.3b0",
            "codecov>=2.0,<3.0",
            "isort>4.0,<5.0",
            "pipdeptree>=0.13,<1.0",
            "pytest-asyncio==0.10.0",
            "pytest-cov>=2.7,<3.0",
            "pytest>=5.0,<6.0",
            "sqlalchemy-utils==0.34.2",
        ],
    },
    entry_points={"console_scripts": ["dms=dms.cli:main"]},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
