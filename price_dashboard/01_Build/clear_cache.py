import shutil
import os

cache_dir = r'C:\Users\BelaZhou\.streamlit\cache'
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print('Cache cleared')
else:
    print('Cache directory not found')