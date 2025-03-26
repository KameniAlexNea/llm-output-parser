from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-output-parser",
    version="0.2.0",
    author="Alex Kameni",
    author_email="Kamenialexnea@gmail.com",
    description="Extract and parse JSON from unstructured text outputs from LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KameniAlexNea/llm-output-parser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    keywords="llm, json, parsing, extraction, nlp, ai, language models",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coveralls>=3.3.1",
        ],
    },
)
