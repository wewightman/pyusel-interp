from setuptools import Extension, setup

# load the C extentsion library
interp = Extension(
    name="interp.engines._cubic1d",
    include_dirs=["interp/engines/"],
    depends=["interp/engines/cubic.h"],
    sources=["interp/engines/cubic.c"]
)

# run setup tools
setup(
    name='pyusel-interp',
    description="C-Backed cubic interpolation engines",
    author_email="wew12@duke.edu",
    packages=['interp', 'interp.engines'],
    package_dir={
        'interp':'interp/', 
        'interp.engines':'interp/engines',
    },
    install_requires = [
        "numpy",
        "pyusel-cinpy @ https://github.com/wewightman/pyusel-cinpy/archive/main.tar.gz",
    ],
    license="MIT",
    ext_modules=[interp],
    version="0.0.0"
)
