from setuptools import setup, find_packages

setup(
    name="aegis-core-lortuarte-sdk",
    version="3.4.0",
    author="LortuArte",
    author_email="hello@aegiscore.dev",
        license="MIT",
    description="Process-local budget authorization and replay-aware execution disposition for Python AI-agent tools.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LortuArte/aegis-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography",
    ],
)