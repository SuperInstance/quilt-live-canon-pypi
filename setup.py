"""setup.py — Live Canon PyPI package"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="quilt-live-canon",
    version="0.9.1",
    description="Live Canon — the AI-Writings canon as a navigable cell fabric. 7 operations: NAVIGATE, CONFLUENCE, LINEAGE, GHOST, TICK, CLAIM, DRILL. Polyformal (Python, JS, C, Rust, Verilog, VHDL). 71 papers bundled. Canonical state hash 0x445185a3a99fd2e7.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Casey Digennaro",
    author_email="superinstance@users.noreply.github.com",
    url="https://github.com/SuperInstance/quilt-live-canon",
    packages=find_packages(),
    include_package_data=True,
    package_data={"live_canon": ["_data.json"]},
    python_requires=">=3.10",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    keywords="quilt cell-fabric polyformalism shape-rag live-canon ai-writings FNV-1a",
)
