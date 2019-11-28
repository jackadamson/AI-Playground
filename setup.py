"""
aiplayground
------------
AI Game Server
"""
import re
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("aiplayground/__init__.py", "r") as f:
    version_match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    )
    if version_match is None:
        raise ValueError("Version not found in aiplayerground/__init__.py")
    version = version_match.group(1)

with open("requirements.txt", "r") as f:
    requirements = [l for l in f.read().split("\n") if len(l) > 0]

with open("requirements-broker.txt", "r") as f:
    requirements_broker = [
        l for l in f.read().split("\n") if len(l) > 2 and l[:2] != "-r"
    ]


setup(
    name="python-socketio",
    version=version,
    url="http://github.com/miguelgrinberg/python-socketio/",
    license="MIT",
    author="Jack Adamson",
    author_email="jack@mrfluffybunny.com",
    description="AI Game Server",
    long_description=long_description,
    packages=["aiplayground"],
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={"broker": requirements_broker},
    # TODO: Add better classifiers
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
