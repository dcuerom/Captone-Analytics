from __future__ import annotations

import glob
import os
import sys
from typing import Iterable


def _norm_path(path: str) -> str:
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def _remove_from_sys_path(target_path: str) -> None:
    target_norm = _norm_path(target_path)
    sys.path[:] = [p for p in sys.path if _norm_path(p) != target_norm]


def _is_readable_file(path: str) -> bool:
    try:
        with open(path, "rb"):
            pass
        return True
    except OSError:
        return False


def _has_package_init(site_dir: str, package_name: str) -> bool:
    init_file = os.path.join(site_dir, package_name, "__init__.py")
    return _is_readable_file(init_file)


def _has_compiled_artifact(site_dir: str, relative_pattern: str) -> bool:
    pattern = os.path.join(site_dir, relative_pattern)
    return any(_is_readable_file(path) for path in glob.glob(pattern))


def _package_is_healthy(site_dir: str, package_name: str) -> bool:
    if not _has_package_init(site_dir, package_name):
        return False

    # Detect common broken installs in `pip --target .pydeps` on Windows.
    if package_name == "numpy":
        return _has_compiled_artifact(site_dir, os.path.join("numpy", "_core", "_multiarray_umath*.pyd"))
    if package_name == "pandas":
        return _has_compiled_artifact(site_dir, os.path.join("pandas", "_libs", "pandas_parser*.pyd"))

    return True


def bootstrap_local_pydeps(required_packages: Iterable[str] = ()) -> str:
    """
    Manage `/.pydeps` in a defensive way.

    Returns:
    - "enabled": `.pydeps` was validated and is active in `sys.path`.
    - "invalid": `.pydeps` exists but is incomplete for required packages.
    - "missing": `.pydeps` does not exist.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    local_deps = os.path.join(project_root, ".pydeps")

    if not os.path.isdir(local_deps):
        return "missing"

    required = [str(p).strip() for p in required_packages if str(p).strip()]
    unhealthy = [pkg for pkg in required if not _package_is_healthy(local_deps, pkg)]
    if unhealthy:
        # Critical safeguard: avoid shadowing a valid env with broken namespace packages
        # or missing compiled artifacts (numpy/pandas on Windows).
        _remove_from_sys_path(local_deps)
        return "invalid"

    if all(_norm_path(p) != _norm_path(local_deps) for p in sys.path):
        # Keep local deps available, but avoid forcing precedence over a healthy active venv.
        sys.path.append(local_deps)
    return "enabled"
