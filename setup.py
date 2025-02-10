from setuptools import setup, find_packages

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(name = "DublinBikes",
      description="Package for the Dublin Bikes project",
      packages=find_packages(),
      install_requires = requirements)

