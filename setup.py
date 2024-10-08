from setuptools import setup, find_packages

setup(
    name="mzkscraper",
    version='1.0',
    packages=find_packages(),
    install_requires=[
        "inflection==0.5.1",
        "nltk==3.9.1",
        "Pillow==10.4.0",
        "Requests==2.32.3",
        "selenium_wire==5.1.0",
        "setuptools==65.5.0",
        "tqdm==4.66.1",
    ],
    author="Vojtech Dvorak",
    url="https://github.com/v-dvorak/mzkscraper",
)
