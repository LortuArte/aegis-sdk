from setuptools import setup, find_packages

setup(
    name='aegis-core-sdk',
    version='3.0.0', # ¡FÍJATE, SIN LA LETRA 'v'!
    description='In-memory L3 Runtime Governance & ACID Policy Gate for AI Agents',
    author='Lortu',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0',
        'requests'
    ],
    python_requires='>=3.8',
)