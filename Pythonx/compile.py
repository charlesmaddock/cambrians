from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("Main",  ["Main_cy.pyx"]),
    Extension("Animal",  ["Animal_cy.pyx"]),
    Extension("Quadtree",  ["Quadtree_cy.pyx"]),
    Extension("Settings",  ["Settings_cy.pyx"]),
]
setup(
    name = 'Cambrians',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)