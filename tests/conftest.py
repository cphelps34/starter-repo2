import sys
import os


def pytest_configure(config):
    # Ensure src/ is on sys.path so tests can import the package when the
    # project isn't installed into the environment.
    tests_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(tests_dir, ".."))
    src_dir = os.path.join(repo_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
