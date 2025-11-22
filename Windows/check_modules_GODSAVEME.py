
import importlib, sys
names=['pkg_resources.py2_warn','dependency_injector.errors',
       'setuptools._distutils._log','setuptools._distutils._modified',
       'setuptools._distutils.compat','setuptools._distutils.compat.numpy',
       'setuptools._distutils.compat.py39','setuptools._distutils.zosccompiler']
for n in names:
    try:
        importlib.import_module(n)
        print(n, "OK")
    except Exception as e:
        print(n, "MISSING:", type(e).__name__, e)
