import os

from flask import current_app

current_dir = os.getcwd()
project_root = current_app.root_path

print(current_app)