"""
===========================================================
PROJECT DASPRO: GAME TEBAK GAMBAR HEWAN (PILIHAN GANDA)
===========================================================
Program ini dibuat menggunakan Python dan pustaka Tkinter,
Pillow (PIL), serta winsound untuk antarmuka grafis (GUI) dan audio.

Fitur-fitur Lengkap:
1. Tombol Suara (Audio Hint) tepat di bawah gambar hewan.
2. Desain serba membulat / lembut (Rounded Capsule & Pill Cards).
3. Palet warna ceria, hangat, dan kontras yang memanjakan mata.
4. Foto hewan dibingkai kartu membulat (Rounded Photo Corners).
5. Tombol pilihan ganda 2x2 berbentuk kapsul bertekstur halus.
6. Efek visual saat menjawab: warna hijau jika benar, merah jika salah.
7. Dukungan klik mouse dan tombol keyboard (A/B/C/D atau 1/2/3/4).
8. Sistem skor, nyawa (❤️ ❤️ ❤️), dan petunjuk teks clue ciri hewan.
===========================================================
"""

import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk

# Audio feature disabled (removed)

# Menentukan direktori dasar tempat script ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "Images")
SOUND_DIR = os.path.join(BASE_DIR, "Sounds")

# ==========================================
# 1. DATABASE SOAL HEWAN
# ==========================================
DATA_HEWAN = [
    {
        "nama": "Gajah",
        "file_gambar": "Gajah.jpg",
        "file_suara": "Gajah.wav",
        "petunjuk": "Hewan darat terbesar yang memiliki belalai panjang dan gading."
    },
    {
        "nama": "Kucing",
        "file_gambar": "Kucing.jpg",
        "file_suara": "Kucing.wav",
        "petunjuk": "Hewan mamalia berbulu lucu yang mengeong dan gemar makan ikan."
    },
    {
        "nama": "Jerapah",
        "file_gambar": "Jerapah.jpg",
        "file_suara": "Jerapah.wav",
        "petunjuk": "Hewan tertinggi di dunia yang memiliki leher sangat panjang dan corak unik."
    },
    {
        "nama": "Singa",
        "file_gambar": "Singa.jpg",
        "file_suara": "Singa.wav",
        "petunjuk": "Dijuluki si raja rimba dengan surai lebat di sekitar lehernya."
    },
    {
        "nama": "Kelinci",
        "file_gambar": "Kelinci.jpg",
        "file_suara": "Kelinci.wav",
        "petunjuk": "Hewan lucu bertelinga panjang yang suka melompat dan makan wortel."
    },
    {
        "nama": "Panda",
        "file_gambar": "Panda.jpg",
        "file_suara": "Panda.wav",
        "petunjuk": "Hewan khas Tiongkok berbulu hitam-putih yang sangat suka memakan bambu."
    },
    {
        "nama": "Rusa",
        "file_gambar": "Rusa.jpg",
        "file_suara": "Rusa.wav",
        "petunjuk": "Hewan berkaki panjang dengan tanduk bercabang di kepala."
    },
    {
        "nama": "Beruang",
        "file_gambar": "Beruang.jpg",
        "file_suara": "Beruang.wav",
        "petunjuk": "Mamalia berukuran besar, berbulu tebal, suka makan madu."
    },
    {
        "nama": "Kuda",
        "file_gambar": "Kuda.jpg",
        "file_suara": "Kuda.wav",
        "petunjuk": "Hewan berkuku satu, terkenal sebagai tunggangan."
    },
    {
        "nama": "Ayam",
        "file_gambar": "Ayam.jpg",
        "file_suara": "Ayam.wav",
        "petunjuk": "Unggas peliharaan yang bertelur dan berbunyi kokok."
    }
]


# ==========================================
# 2. HELPER PEMBUAT GRAFIK MEMBULAT (PILL / CAPSULE)
# ==========================================
def buat_kapsul(w, h, r, fill, outline=None, border_width=2, bg_parent="#FFFBEB"):
    """
    Menghasilkan gambar kapsul membulat dengan teknik 2x supersampling (antialiasing)
    sehingga sudut-sudutnya sangat halus dan tidak kotak tajam.
    """
    scale = 2
    sw, sh, sr = w * scale, h * scale, r * scale
    im = Image.new("RGB", (sw, sh), bg_parent)
    draw = ImageDraw.Draw(im)

    if outline and border_width > 0:
        draw.rounded_rectangle(
            [0, 0, sw - 1, sh - 1],
            radius=sr,
            fill=fill,
            outline=outline,
            width=border_width * scale
        )
    else:
        draw.rounded_rectangle(
            [0, 0, sw - 1, sh - 1],
            radius=sr,
            fill=fill
        )

    im_resized = im.resize((w, h), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(im_resized)


def buat_kartu_gambar(card_w, card_h, card_r, card_bg, border_color, photo_path, fallback_text="", bg_parent="#FFFBEB"):
    """
    Membuat kartu foto dengan sudut-sudut membulat halus, membingkai foto hewan
    sehingga tidak ada sudut kotak tajam sama sekali.
    """
    scale = 2
    cw, ch, cr = card_w * scale, card_h * scale, card_r * scale
    card = Image.new("RGB", (cw, ch), bg_parent)
    draw = ImageDraw.Draw(card)

    # Gambar latar belakang kartu membulat
    draw.rounded_rectangle(
        [0, 0, cw - 1, ch - 1],
        radius=cr,
        fill=card_bg,
        outline=border_color,
        width=3 * scale
    )

    # Masukkan foto hewan jika ada
    photo_loaded = False
    if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
        try:
            im = Image.open(photo_path).convert("RGBA")
            max_w = (card_w - 40) * scale
            max_h = (card_h - 30) * scale
            im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

            # Buat mask membulat untuk foto hewan
            mask = Image.new("L", im.size, 0)
            mdraw = ImageDraw.Draw(mask)
            mdraw.rounded_rectangle(
                [0, 0, im.width - 1, im.height - 1],
                radius=18 * scale,
                fill=255
            )

            # Tempel di tengah kartu
            px = (cw - im.width) // 2
            py = (ch - im.height) // 2
            card.paste(im, (px, py), mask)
            photo_loaded = True
        except Exception:
            photo_loaded = False

    # Jika foto gagal dimuat, buat placeholder membulat
    if not photo_loaded:
        draw.text(
            (cw // 2, ch // 2),
            fallback_text or "[Gambar Belum Tersedia]",
            fill="#9CA3AF",
            anchor="mm"
        )

    card_final = card.resize((card_w, card_h), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(card_final)


# ==========================================
# 3. KELAS UTAMA PERMAINAN
# ==========================================
class GameTebakGambar:
    def __init__(self, root):
        self.root = root
        self.root.title("🐾 Tebak Gambar Hewan - Fitur Hint Suara! 🎵")
        self.root.geometry("680x830")
        self.root.resizable(False, False)

        # Palet Warna Hangat & Ceria
        self.WARNA_BG = "#FFFBEB"          # Kuning lembut / Cream cerah
        self.WARNA_HEADER = "#FF5E7E"      # Pink stroberi ceria
        self.WARNA_CARD = "#FFFFFF"        # Putih bersih
        self.WARNA_KUNING = "#FEF08A"      # Kuning lemon untuk petunjuk
        self.WARNA_HIJAU = "#10B981"       # Hijau cerah untuk jawaban benar
        self.WARNA_MERAH = "#EF4444"       # Merah cerah untuk jawaban salah
        self.WARNA_ORANYE = "#F59E0B"      # Oranye ceria
        self.WARNA_UNGU = "#8B5CF6"        # Ungu lilac ceria
        self.WARNA_CYAN = "#0284C7"        # Biru toska ceria untuk tombol suara
        self.WARNA_TEKS = "#1F2937"        # Teks gelap tajam

        self.root.configure(bg=self.WARNA_BG)

        # Variabel Status Permainan
        self.skor = 0
        self.nyawa = 3
        self.indeks_soal = 0
        self.daftar_soal = []
        self.pilihan_sekarang = []
        self.jawaban_terkunci = False
        self.petunjuk_dibuka = False

        # Cache Gambar Kapsul (Garbage Collection Guard)
        self.img_header = None
        self.img_badge_soal = None
        self.img_badge_nyawa = None
        self.img_badge_skor = None
        self.img_kartu_foto = None
        self.img_btn_suara_normal = None
        self.img_btn_suara_aktif = None
        self.img_kotak_petunjuk = None
        self.img_btn_petunjuk = None
        self.img_btn_lewati = None

        # Cache untuk Opsi Tombol A, B, C, D
        self.cache_opsi_normal = []
        self.img_opsi_benar = None
        self.img_opsi_salah = None

        # Data Style Opsi (Warna-warni pastel membulat)
        self.style_opsi = [
            {"label": "A", "bg": "#EFF6FF", "border": "#3B82F6", "fg": "#1E40AF"},
            {"label": "B", "bg": "#ECFDF5", "border": "#10B981", "fg": "#065F46"},
            {"label": "C", "bg": "#FFF7ED", "border": "#F97316", "fg": "#9A3412"},
            {"label": "D", "bg": "#FAF5FF", "border": "#A855F7", "fg": "#6B21A8"}
        ]

        # Inisialisasi antarmuka dan mulai permainan
        self.buat_antarmuka()
        self.pasang_shortcut_keyboard()
        self.mulai_permainan()

    # ==========================================
    # 4. PEMBUATAN ANTARMUKA PENGGUNA (GUI MEMBULAT)
    # ==========================================
    def buat_antarmuka(self):
        # 1. Header Kapsul Membulat
        self.img_header = buat_kapsul(620, 58, 26, self.WARNA_HEADER, outline="#F43F5E", bg_parent=self.WARNA_BG)
        label_header = tk.Label(
            self.root,
            image=self.img_header,
            text="✨ 🐾 GAME TEBAK GAMBAR HEWAN 🐾 ✨",
            compound="center",
            font=("Times New Roman", 15, "bold"),
            fg="white",
            bg=self.WARNA_BG,
            bd=0
        )
        label_header.pack(pady=(10, 4))

        # 2. Baris Status (Soal, Nyawa, Skor) dengan Kapsul Membulat
        frame_status = tk.Frame(self.root, bg=self.WARNA_BG)
        frame_status.pack(pady=4)

        # Badge Soal
        self.img_badge_soal = buat_kapsul(140, 36, 18, "#EEF2FF", outline="#818CF8", bg_parent=self.WARNA_BG)
        self.label_level = tk.Label(
            frame_status,
            image=self.img_badge_soal,
            text="🎯 Soal: 1/6",
            compound="center",
            font=("Times New Roman", 11, "bold"),
            fg="#4338CA",
            bg=self.WARNA_BG,
            bd=0
        )
        self.label_level.grid(row=0, column=0, padx=8)

        # Badge Nyawa
        self.img_badge_nyawa = buat_kapsul(210, 36, 18, "#FFE4E6", outline="#FB7185", bg_parent=self.WARNA_BG)
        self.label_nyawa = tk.Label(
            frame_status,
            image=self.img_badge_nyawa,
            text="Nyawa: ❤️ ❤️ ❤️",
            compound="center",
            font=("Times New Roman", 11, "bold"),
            fg="#E11D48",
            bg=self.WARNA_BG,
            bd=0
        )
        self.label_nyawa.grid(row=0, column=1, padx=8)

        # Badge Skor
        self.img_badge_skor = buat_kapsul(140, 36, 18, "#DCFCE7", outline="#4ADE80", bg_parent=self.WARNA_BG)
        self.label_skor = tk.Label(
            frame_status,
            image=self.img_badge_skor,
            text="⭐ Skor: 0",
            compound="center",
            font=("Times New Roman", 11, "bold"),
            fg="#15803D",
            bg=self.WARNA_BG,
            bd=0
        )
        self.label_skor.grid(row=0, column=2, padx=8)

        # 3. Area Gambar Hewan & Tombol Suara di Sampingnya
        frame_gambar_suara = tk.Frame(self.root, bg=self.WARNA_BG)
        frame_gambar_suara.pack(pady=(4, 4))

        # Kartu Gambar Hewan (Bentuk Membulat Halus)
        self.label_gambar = tk.Label(frame_gambar_suara, bg=self.WARNA_BG, bd=0)
        self.label_gambar.pack(side=tk.LEFT, padx=(0, 12))



        # 5. Kotak Petunjuk Kapsul Membulat
        self.img_kotak_petunjuk = buat_kapsul(610, 48, 20, self.WARNA_KUNING, outline="#F59E0B", border_width=2, bg_parent=self.WARNA_BG)
        self.label_teks_petunjuk = tk.Label(
            self.root,
            image=self.img_kotak_petunjuk,
            text="💡 Petunjuk teks terkunci. Klik 'Buka Petunjuk' jika butuh clue tambahan.",
            compound="center",
            font=("Times New Roman", 10, "italic"),
            fg="#854D0E",
            bg=self.WARNA_BG,
            wraplength=550,
            justify=tk.CENTER,
            bd=0
        )
        self.label_teks_petunjuk.pack(pady=3)

        # 6. Label Instruksi Pilihan Ganda
        label_instruksi = tk.Label(
            self.root,
            text="👇 Tebak nama hewan di atas (Pilih salah satu):",
            font=("Times New Roman", 11, "bold"),
            bg=self.WARNA_BG,
            fg="#1F2937"
        )
        label_instruksi.pack(pady=(4, 3))

        # 7. Kontainer Tombol Pilihan Ganda (Grid 2x2 Kapsul Membulat)
        frame_pilihan = tk.Frame(self.root, bg=self.WARNA_BG)
        frame_pilihan.pack(pady=2)

        # Pre-generate gambar kapsul untuk tombol
        self.cache_opsi_normal = []
        for opt in self.style_opsi:
            img = buat_kapsul(285, 50, 22, opt["bg"], outline=opt["border"], border_width=2, bg_parent=self.WARNA_BG)
            self.cache_opsi_normal.append(img)

        self.img_opsi_benar = buat_kapsul(285, 50, 22, self.WARNA_HIJAU, outline="#059669", border_width=2, bg_parent=self.WARNA_BG)
        self.img_opsi_salah = buat_kapsul(285, 50, 22, self.WARNA_MERAH, outline="#DC2626", border_width=2, bg_parent=self.WARNA_BG)

        self.tombol_pilihan = []
        for i in range(4):
            baris = i // 2
            kolom = i % 2
            btn = tk.Button(
                frame_pilihan,
                image=self.cache_opsi_normal[i],
                text=f"{self.style_opsi[i]['label']}. ...",
                compound="center",
                font=("Times New Roman", 12, "bold"),
                fg=self.style_opsi[i]["fg"],
                bg=self.WARNA_BG,
                activebackground=self.WARNA_BG,
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda idx=i: self.pilih_jawaban(idx)
            )
            btn.grid(row=baris, column=kolom, padx=8, pady=4)
            self.tombol_pilihan.append(btn)

        # 8. Label Pesan Feedback (Benar / Salah)
        self.label_pesan = tk.Label(
            self.root,
            text="",
            font=("Times New Roman", 11, "bold"),
            bg=self.WARNA_BG,
            fg=self.WARNA_TEKS
        )
        self.label_pesan.pack(pady=4)

        # 9. Tombol Bawah (Petunjuk & Lewati Soal) Kapsul Membulat
        frame_bawah = tk.Frame(self.root, bg=self.WARNA_BG)
        frame_bawah.pack(pady=3)

        self.img_btn_petunjuk = buat_kapsul(210, 40, 20, self.WARNA_ORANYE, outline="#D97706", bg_parent=self.WARNA_BG)
        btn_petunjuk = tk.Button(
            frame_bawah,
            image=self.img_btn_petunjuk,
            text="💡 Buka Petunjuk (-5)",
            compound="center",
            font=("Times New Roman", 10, "bold"),
            fg="white",
            bg=self.WARNA_BG,
            activebackground=self.WARNA_BG,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self.buka_petunjuk
        )
        btn_petunjuk.grid(row=0, column=0, padx=10)

        self.img_btn_lewati = buat_kapsul(190, 40, 20, self.WARNA_UNGU, outline="#7C3AED", bg_parent=self.WARNA_BG)
        btn_lewati = tk.Button(
            frame_bawah,
            image=self.img_btn_lewati,
            text="⏩ Lewati Soal Ini",
            compound="center",
            font=("Times New Roman", 10, "bold"),
            fg="white",
            bg=self.WARNA_BG,
            activebackground=self.WARNA_BG,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self.lewati_soal
        )
        btn_lewati.grid(row=0, column=1, padx=10)

    # ==========================================
    # 5. SHORTCUT KEYBOARD (A/B/C/D atau 1/2/3/4 atau Spasi)
    # ==========================================
    def pasang_shortcut_keyboard(self):
        for k in ("a", "A", "1"):
            self.root.bind(f"<Key-{k}>", lambda e: self.pilih_jawaban(0))
        for k in ("b", "B", "2"):
            self.root.bind(f"<Key-{k}>", lambda e: self.pilih_jawaban(1))
        for k in ("c", "C", "3"):
            self.root.bind(f"<Key-{k}>", lambda e: self.pilih_jawaban(2))
        for k in ("d", "D", "4"):
            self.root.bind(f"<Key-{k}>", lambda e: self.pilih_jawaban(3))
        # Tombol Spasi atau S untuk memutar suara
        for k in ("space", "s", "S"):
            self.root.bind(f"<Key-{k}>", lambda e: self.putar_suara_hewan())

    # ==========================================
    # 6. LOGIKA AUDIO & PERMAINAN
    # ==========================================
    def putar_suara_hewan(self):
        """Memutar file suara hewan sebagai petunjuk (hint audio) tanpa membekukan GUI."""
        if not AUDIO_TERSEDIA:
            self.label_pesan.config(text="⚠️ Fitur suara tidak didukung pada sistem ini.", fg="#DC2626")
            return

        if self.indeks_soal >= len(self.daftar_soal):
            return

        soal_sekarang = self.daftar_soal[self.indeks_soal]
        nama_file = soal_sekarang.get("file_suara", "")
        jalur_suara = os.path.join(SOUND_DIR, nama_file)

        if os.path.exists(jalur_suara) and os.path.getsize(jalur_suara) > 0:
            try:
                # Putar suara secara asynchronous agar aplikasi tetap lancar
                winsound.PlaySound(jalur_suara, winsound.SND_FILENAME | winsound.SND_ASYNC)

                # Ubah tampilan tombol sesaat untuk efek feedback visual
                self.btn_suara.config(
                    image=self.img_btn_suara_aktif,
                    text="🎶\nMemutar\nSuara... 🔊",
                    fg="white"
                )
                self.root.after(1600, self.reset_tampilan_tombol_suara)
            except Exception as e:
                self.label_pesan.config(text=f"Gagal memutar audio: {e}", fg="#DC2626")
        else:
            self.label_pesan.config(text="Audio suara hewan ini belum tersedia.", fg="#9CA3AF")

    def reset_tampilan_tombol_suara(self):
        """No audio button; method stub."""
        pass

    def mulai_permainan(self):
        """Memulai sesi permainan baru dengan mengacak urutan soal."""
        self.skor = 0
        self.nyawa = 3
        self.indeks_soal = 0
        self.daftar_soal = list(DATA_HEWAN)
        random.shuffle(self.daftar_soal)
        self.perbarui_status()
        self.tampilkan_soal()

    def perbarui_status(self):
        """Memperbarui label skor, nyawa, dan level."""
        self.label_skor.config(text=f"⭐ Skor: {self.skor}")
        hati = "❤️ " * self.nyawa if self.nyawa > 0 else "💀 Habis"
        self.label_nyawa.config(text=f"Nyawa: {hati}")
        total = len(self.daftar_soal)
        nomor = min(self.indeks_soal + 1, total)
        self.label_level.config(text=f"🎯 Soal: {nomor}/{total}")

    def tampilkan_soal(self):
        """Menyiapkan soal baru, kartu gambar membulat, dan 4 pilihan ganda."""
        if self.indeks_soal >= len(self.daftar_soal):
            self.selesai_permainan(menang=True)
            return

        self.jawaban_terkunci = False
        self.petunjuk_dibuka = False
        soal_sekarang = self.daftar_soal[self.indeks_soal]
        jawaban_benar = soal_sekarang["nama"]

        self.reset_tampilan_tombol_suara()
        self.label_teks_petunjuk.config(
            text="💡 Petunjuk teks terkunci. Klik 'Buka Petunjuk' jika butuh clue tambahan."
        )
        self.label_pesan.config(text="")
        self.perbarui_status()

        # Memuat kartu gambar hewan membulat
        jalur_gambar = os.path.join(IMAGE_DIR, soal_sekarang["file_gambar"])
        self.img_kartu_foto = buat_kartu_gambar(
            card_w=480,
            card_h=265,
            card_r=24,
            card_bg="#FFFFFF",
            border_color="#FDE68A",
            photo_path=jalur_gambar,
            fallback_text=f"Foto {jawaban_benar}",
            bg_parent=self.WARNA_BG
        )
        self.label_gambar.config(image=self.img_kartu_foto)

        # Buat 4 opsi pilihan ganda (1 benar + 3 pengecoh)
        semua_hewan = [h["nama"] for h in DATA_HEWAN if h["nama"] != jawaban_benar]
        pengecoh = random.sample(semua_hewan, min(3, len(semua_hewan)))
        opsi = [jawaban_benar] + pengecoh
        random.shuffle(opsi)
        self.pilihan_sekarang = opsi

        # Reset 4 tombol kapsul ke tampilan normal
        for i in range(4):
            btn = self.tombol_pilihan[i]
            nama_hewan = self.pilihan_sekarang[i]
            label_huruf = self.style_opsi[i]["label"]
            btn.config(
                image=self.cache_opsi_normal[i],
                text=f"{label_huruf}.  {nama_hewan}",
                fg=self.style_opsi[i]["fg"],
                state=tk.NORMAL
            )

    def buka_petunjuk(self):
        """Membuka petunjuk ciri-ciri hewan dengan sedikit penalti poin."""
        if self.petunjuk_dibuka or self.jawaban_terkunci:
            return

        self.petunjuk_dibuka = True
        soal_sekarang = self.daftar_soal[self.indeks_soal]
        self.label_teks_petunjuk.config(
            text=f"💡 Clue: {soal_sekarang['petunjuk']} (Huruf awal: '{soal_sekarang['nama'][0]}')"
        )
        if self.skor >= 5:
            self.skor -= 5
        self.perbarui_status()

    def pilih_jawaban(self, idx):
        """Memproses jawaban pilihan ganda pengguna."""
        if self.jawaban_terkunci or idx >= len(self.pilihan_sekarang):
            return

        self.jawaban_terkunci = True  # Kunci agar tidak bisa spam klik
        soal_sekarang = self.daftar_soal[self.indeks_soal]
        jawaban_benar = soal_sekarang["nama"]
        jawaban_dipilih = self.pilihan_sekarang[idx]
        tombol_dipilih = self.tombol_pilihan[idx]

        idx_benar = self.pilihan_sekarang.index(jawaban_benar)

        if jawaban_dipilih == jawaban_benar:
            # Jawaban Benar -> Kapsul berubah Hijau Segar
            tombol_dipilih.config(image=self.img_opsi_benar, fg="white")
            poin = 20 if not self.petunjuk_dibuka else 15
            self.skor += poin
            self.label_pesan.config(
                text=f"🎉 BENAR SEKALI! Itu adalah {jawaban_benar} (+{poin} poin)",
                fg="#059669"
            )
            self.root.after(1200, self.soal_berikutnya)
        else:
            # Jawaban Salah -> Kapsul yang dipilih Merah, jawaban yang benar Hijau
            tombol_dipilih.config(image=self.img_opsi_salah, fg="white")
            self.tombol_pilihan[idx_benar].config(image=self.img_opsi_benar, fg="white")

            self.nyawa -= 1
            self.perbarui_status()

            if self.nyawa <= 0:
                self.label_pesan.config(
                    text=f"💥 Nyawa habis! Jawaban yang benar adalah: {jawaban_benar}",
                    fg="#E11D48"
                )
                self.root.after(1500, lambda: self.selesai_permainan(menang=False))
            else:
                self.label_pesan.config(
                    text=f"❌ Kurang tepat! Jawaban yang benar: {jawaban_benar} (Sisa nyawa: {self.nyawa})",
                    fg="#E11D48"
                )
                self.root.after(1500, self.soal_berikutnya)

    def lewati_soal(self):
        """Melewati soal saat ini dan mengurangi satu nyawa."""
        if self.jawaban_terkunci:
            return

        self.jawaban_terkunci = True
        soal_sekarang = self.daftar_soal[self.indeks_soal]
        self.nyawa -= 1
        self.perbarui_status()
        self.label_pesan.config(
            text=f"⏩ Soal dilewati! Jawabannya adalah: {soal_sekarang['nama']}",
            fg="#6B7280"
        )
        if self.nyawa <= 0:
            self.root.after(1500, lambda: self.selesai_permainan(menang=False))
        else:
            self.root.after(1200, self.soal_berikutnya)

    def soal_berikutnya(self):
        """Melanjutkan ke soal berikutnya."""
        self.indeks_soal += 1
        self.tampilkan_soal()

    def selesai_permainan(self, menang):
        """Menampilkan dialog hasil akhir dan menawarkan bermain kembali."""
        if menang:
            pesan = f"🏆 HOREEE! KAMU MENANG! 🏆\n\nKamu berhasil menyelesaikan semua soal hewan!\n⭐ Skor Akhir: {self.skor}\n💖 Sisa Nyawa: {self.nyawa}\n\nIngin bermain lagi?"
            judul = "🎉 Selamat! Kemenangan Spektakuler!"
        else:
            pesan = f"💀 GAME OVER! 💀\n\nNyawamu telah habis.\n⭐ Skor Akhir: {self.skor}\n\nJangan menyerah, mau coba main lagi?"
            judul = "Game Over - Coba Lagi!"

        ulang = messagebox.askyesno(judul, pesan)
        if ulang:
            self.mulai_permainan()
        else:
            # Kembali ke halaman menu
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.geometry("680x830")
            MenuUtama(self.root)


# ==========================================
# 7. HALAMAN MENU UTAMA
# ==========================================
class MenuUtama:
    def __init__(self, root):
        self.root = root
        self.root.title("🐾 Tebak Gambar Hewan")
        self.root.geometry("680x830")
        self.root.resizable(False, False)

        self.WARNA_BG     = "#FFFBEB"
        self.WARNA_HEADER = "#FF5E7E"
        self.WARNA_HIJAU  = "#10B981"
        self.WARNA_MERAH  = "#EF4444"
        self.WARNA_UNGU   = "#8B5CF6"
        self.WARNA_TEKS   = "#1F2937"

        self.root.configure(bg=self.WARNA_BG)

        # Cache gambar agar tidak di-GC
        self._imgs = []

        self._buat_menu()

    def _simpan(self, img):
        self._imgs.append(img)
        return img

    def _buat_menu(self):
        # --- Header ---
        img_header = self._simpan(
            buat_kapsul(620, 70, 28, self.WARNA_HEADER,
                        outline="#F43F5E", bg_parent=self.WARNA_BG)
        )
        tk.Label(
            self.root,
            image=img_header,
            text="✨ 🐾 GAME TEBAK GAMBAR HEWAN 🐾 ✨",
            compound="center",
            font=("Times New Roman", 17, "bold"),
            fg="white",
            bg=self.WARNA_BG, bd=0
        ).pack(pady=(30, 10))

        # --- Subjudul ---
        tk.Label(
            self.root,
            text="Uji pengetahuanmu tentang dunia hewan! 🌿",
            font=("Times New Roman", 12, "italic"),
            fg="#78716C",
            bg=self.WARNA_BG
        ).pack(pady=(0, 30))

        # --- Aturan singkat ---
        frame_info = tk.Frame(self.root, bg="#FEF3C7", bd=0)
        frame_info.pack(pady=(0, 30), padx=60, fill="x")

        aturan = (
            "🎯  Jawab soal pilihan ganda dengan benar\n"
            "❤️   Kamu punya 3 nyawa — jaga baik-baik!\n"
            "⭐  Jawaban benar = +20 poin  |  Pakai petunjuk = +15 poin\n"
            "⏩  Lewati soal = kehilangan 1 nyawa"
        )
        tk.Label(
            frame_info,
            text=aturan,
            font=("Times New Roman", 11),
            fg=self.WARNA_TEKS,
            bg="#FEF3C7",
            justify="left",
            padx=20, pady=14
        ).pack()

        # --- Tombol Mulai ---
        img_mulai = self._simpan(
            buat_kapsul(220, 50, 24, self.WARNA_HIJAU,
                        outline="#059669", bg_parent=self.WARNA_BG)
        )
        tk.Button(
            self.root,
            image=img_mulai,
            text="▶  Mulai Bermain",
            compound="center",
            font=("Times New Roman", 13, "bold"),
            fg="white",
            bg=self.WARNA_BG,
            activebackground=self.WARNA_BG,
            bd=0, highlightthickness=0, cursor="hand2",
            command=self._mulai
        ).pack(side="left", padx=(110, 10), pady=10)

        # --- Tombol Keluar ---
        img_keluar = self._simpan(
            buat_kapsul(180, 50, 24, self.WARNA_MERAH,
                        outline="#DC2626", bg_parent=self.WARNA_BG)
        )
        tk.Button(
            self.root,
            image=img_keluar,
            text="✖  Keluar",
            compound="center",
            font=("Times New Roman", 13, "bold"),
            fg="white",
            bg=self.WARNA_BG,
            activebackground=self.WARNA_BG,
            bd=0, highlightthickness=0, cursor="hand2",
            command=self.root.destroy
        ).pack(side="left", padx=(10, 0), pady=10)

    def _mulai(self):
        # Hapus semua widget menu, lalu jalankan game di window yang sama
        for widget in self.root.winfo_children():
            widget.destroy()
        GameTebakGambar(self.root)


# ==========================================
# 8. ENTRY POINT PROGRAM
# ==========================================
if __name__ == "__main__":
    jendela_utama = tk.Tk()
    MenuUtama(jendela_utama)
    jendela_utama.mainloop()
