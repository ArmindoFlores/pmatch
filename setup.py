import glob

import setuptools
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "_pmatch",
        sorted(glob.glob("src/*.cpp")),
    ),
]

setuptools.setup(
    name="pmatch",
    version="0.0.1",
    author="Francisco Rodrigues",
    author_email="francisco.rodrigues0908@gmail.com",
    description="A regex-like way of pattern-matching python objects",
    python_requires=">=3.8",
    packages=setuptools.find_packages(),
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules
)
