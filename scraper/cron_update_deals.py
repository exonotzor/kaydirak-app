"""
Kaydırak - Otomatik Katalog Rotasyon Köprüsü
Eski 'cron_update_deals.py' çağrılarını yeni 'backend/rotation_engine.py' motoruna yönlendirir.
Böylece eski Ekim ayı kataloğunun (hatalı görselli/fiyatlı ürünlerin) geri yüklenmesi engellenir.
"""

import os
import sys
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(PROJECT_DIR)

if __name__ == '__main__':
    engine_path = os.path.join(PROJECT_DIR, 'backend', 'rotation_engine.py')
    res = subprocess.run([sys.executable, engine_path], cwd=PROJECT_DIR)
    sys.exit(res.returncode)
