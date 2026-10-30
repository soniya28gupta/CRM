import os
import sys
import pytest

if __name__ == "__main__":
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, backend_dir)
    print(f"Running pytest with PYTHONPATH: {backend_dir}")
    exit_code = pytest.main(["-v", os.path.join(backend_dir, "tests")])
    sys.exit(exit_code)

