from setuptools import Extension, setup

# load the C extentsion library
interp = Extension(
    name="interp.engines.cubic1d._cubic1d",
    include_dirs=["interp/engines/"],
    depends=["interp/engines/cubic.h"],
    sources=["interp/engines/cubic.c"]
)

# run setup tools
setup(
    name='pyusel-cubic-interp',
    description="C-Backed cubic interpolation engines",
    author_email="wew12@duke.edu",
    packages=['interp', 'interp.engines', 'interp.engines.cubic1d', 'interp.engines.cubic1d._cubic1d'],
    package_dir={
        'interp':'interp/', 
        'interp.engines':'interp/engines',
        'interp.engines.cubic1d':'interp/engines',
        'interp.engines.cubic1d._cubic1d':'interp/engines',
    },
    license="MIT",
    ext_modules=[interp],
    version="0.0.0"
)