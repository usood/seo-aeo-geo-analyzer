import os
import glob


def _reports_root():
    return os.path.realpath(os.path.join(os.getcwd(), "reports"))


def _safe_report_path(path):
    """Return a normalized reports subdirectory path, or None if unsafe."""
    if not path:
        return None

    candidate = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
    candidate = os.path.realpath(candidate)
    reports_root = _reports_root()

    if not os.path.isdir(candidate):
        return None

    if candidate == reports_root or candidate.startswith(reports_root + os.sep):
        return candidate

    return None

def get_current_project_path():
    """Get the path to the current project's report directory"""
    if os.path.exists('.latest_project'):
        with open('.latest_project', 'r') as f:
            path = f.read().strip()
            safe_path = _safe_report_path(path)
            if safe_path:
                return safe_path
    return "." # Fallback to root

def get_latest_file(pattern, directory=None):
    """Find latest file matching pattern in directory"""
    if directory is None:
        directory = get_current_project_path()
        
    full_pattern = os.path.join(directory, pattern)
    files = glob.glob(full_pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)
