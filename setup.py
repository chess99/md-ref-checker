"""
Setup script for Markdown reference checker
"""

from setuptools import setup, find_packages

setup(
    name='md-ref-checker',
    version='0.1.0',
    description='检查 Markdown 文件中的引用完整性',
    author='ZCS',
    author_email='zcs@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'md-ref-checker=checker.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing :: Markup :: Markdown',
        'Topic :: Utilities',
    ],
) 