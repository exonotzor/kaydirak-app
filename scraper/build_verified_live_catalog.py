"""
Devre dışı bırakıldı: Eski katalog oluşturucu yerine backend/rotation_engine.py kullanılmaktadır.
"""
import os
import sys
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
engine_path = os.path.join(PROJECT_DIR, 'backend', 'rotation_engine.py')
subprocess.run([sys.executable, engine_path], cwd=PROJECT_DIR)
