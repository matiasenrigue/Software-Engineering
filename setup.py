from setuptools import setup, find_packages

with open("requirements.txt") as f:
    content = f.readlines()

requirements = [
    line.strip()
    for line in content
    if line.strip() and not line.startswith("-e git+ssh://git@github.com/matiasenrigue")
]

setup(
    name="DublinBikes",
    description="Package for the Dublin Bikes project",
    packages=find_packages(),
    install_requires=requirements,
)
