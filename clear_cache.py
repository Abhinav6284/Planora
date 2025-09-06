import shutil
import os

def clear_pycache(start_path):
    for root, dirs, files in os.walk(start_path):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                print(f'Removing {pycache_path}')
                shutil.rmtree(pycache_path)
        for file_name in files:
            if file_name.endswith('.pyc') or file_name.endswith('.pyo'):
                file_path = os.path.join(root, file_name)
                print(f'Removing {file_path}')
                os.remove(file_path)

clear_pycache('.')
print("Cache cleared!")
