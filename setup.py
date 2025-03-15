from setuptools import setup, find_packages

setup(
    name="uranus",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "openai>=1.0.0",
        "psutil>=5.9.0",
        "aiohttp>=3.8.0",
        "browser_use>=0.1.40",
    ],
    entry_points={
        "console_scripts": [
            "uranus=uranus.main:main",
        ],
    },
    author="Uranus Team",
    author_email="",
    description="A reactive agent system based on Manus",
    keywords="ai, agent, reactive",
    python_requires=">=3.10",
)