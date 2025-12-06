import os
import glob

def get_current_project_path():
    """Get the path to the current project's report directory"""
    if os.path.exists('.latest_project'):
        with open('.latest_project', 'r') as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
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
