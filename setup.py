from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="md-ref-checker",
    version="0.1.0",
    author="zcs",
    author_email="",  # Add your email if you want
    description="A tool for checking references in Markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/md-ref-checker",  # Update with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "markdown-it-py>=3.0.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "md-ref-checker=src.check_references:main",
        ],
    },
    package_data={
        "md_ref_checker": ["py.typed"],
    },
) 