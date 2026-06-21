from setuptools import setup, find_packages

setup(
    name='aegis-core-sdk',
    version='3.0.3',  # Saltamos a 3.0.3 para evitar conflictos de historial
    description='In-memory L3 Runtime Governance & ACID Policy Gate for AI Agents',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Lortu',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'cryptography>=41.0.0',
        'requests>=2.31.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)