from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ebook-manager",
    version="0.1.0",
    author="OttScott",
    author_email="your.email@example.com",
    description="Advanced ebook collection management utility with beets integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OttScott/ebook-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No hard dependencies - beets is optional
    ],
    extras_require={
        "beets": [
            "beets>=1.6.0",
            "beets-ebooks",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "flake8",
            "black",
            "isort",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "ebook-manager=ebook_manager:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
