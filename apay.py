# Game Tebak Gambar Hewan - Project Daspro
# File ini terhubung langsung ke modul utama main.py

import os
import sys

# Menambahkan direktori aktif ke sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import MenuUtama, tk

if __name__ == "__main__":
    jendela_utama = tk.Tk()
    MenuUtama(jendela_utama)
    jendela_utama.mainloop()

