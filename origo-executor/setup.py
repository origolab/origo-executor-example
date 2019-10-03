from distutils.core import setup
from Cython.Build import cythonize

setup(
    name="Origo Executor",
    ext_modules=cythonize(["executor_service/*.py", "executor/*.py", "executor/*/*.py", "executor/*/*/*.py"],
                          exclude=["executor_service/run_executor_service.py", "executor/constants/*"]))
