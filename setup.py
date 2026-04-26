from setuptools import setup, find_packages

setup(
    name="paml",
    version="1.0.0",
    description="PAML — Persistent Agent Memory Layer. Cross-platform memory for AI agents.",
    author="Anurag",
    py_modules=["paml"],
    entry_points={
        "console_scripts": ["paml=paml:main"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)