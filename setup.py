"""
Configuration du package
"""
from setuptools import setup, find_packages

setup(
    name="universal-code-agent",
    version="2.0.0",
    description="Agent IA universel modulaire pour génération de code",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "streamlit>=1.29.0",
    ],
    extras_require={
        "full": [
            "langchain>=0.3.20",
            "langchain-core>=0.3.60",
            "langchain-community>=0.3.20",
            "langchain-chroma>=0.2.4",
            "langchain-huggingface>=0.1.0",
            "langchain-ollama>=0.2.0",
            "chromadb>=1.0.0",
            "sentence-transformers>=2.2.2",
            "plotly>=5.17.0",
            "pandas>=2.0.3",
        ]
    },
    entry_points={
        "console_scripts": [
            "universal-agent=cli.main:main",
        ],
    },
)