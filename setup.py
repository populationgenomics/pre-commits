"""Setup file to install the pre-commit hook."""

from setuptools import setup

PKG = 'pre_commit_hooks'

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="cpg-pre-commit-hooks",
    version="1.0.0",
    description="Pre-commit hook to check for CPG / XPG IDs in staged files.",
    url="",
    author="Centre for Population Genomics",
    author_email="",
    license="MIT",
    packages=["pre_commit_hooks"],
    install_requires=[],
    entry_points={
        "console_scripts": ["cpg_id_checker = pre_commit_hooks.cpg_id_checker:main"],
    },
)
