from setuptools import setup, find_packages

setup(
    name='aegis-sdk-salesforce',
    version='2.1.0', # Sube la versión a 2.1.0 para que PyPI la acepte como nueva
    description='L3 Policy Gate for Autonomous AI Agents in Salesforce (0.005ms ACID locks)',
    author='Lortu',
    packages=find_packages(),
    install_requires=[
        'cryptography>=41.0.0', # VITAL PARA ED25519
        'requests'
    ],
    python_requires='>=3.8',
)
