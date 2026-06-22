from setuptools import setup, find_packages

setup(
    name="aegis-core-sdk",
    version="3.1.0", # Saltamos a la v3.1 por marketing (parece más maduro)
    author="LortuArte",
    author_email="hello@aegiscore.dev", # Cambia esto si quieres
    description="Sub-millisecond Tool-Execution Firewall to prevent AI Agent Double-Spending.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TuUsuario/aegis-core", # ACTUALIZA CON TU LINK REAL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[], # Mantenlo ligero, 0 dependencias es tu fuerte
)