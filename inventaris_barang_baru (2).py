# Program Inventaris Barang

import json
import os
from datetime import datetime, timedelta
from getpass import getpass

DATA_DIR = "data_inventaris"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
BORROWS_FILE = os.path.join(DATA_DIR, "borrows.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")

ADMINS = {
    "Rio": "rio123",
    "Alfan": "alfan123"
}

DEFAULT_LOAN_DAYS = 1

os.makedirs(DATA_DIR, exist_ok=True)


# ================== UTIL & VALIDASI ==================
def input_nonempty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Input tidak boleh kosong!")

def input_int(prompt, min_value=None):
    while True:
        v = input(prompt)
        if v.isdigit():
            v = int(v)
            if min_value is not None and v < min_value:
                print(f"Masukkan angka >= {min_value}")
                continue
            return v
        print("Input harus angka!")

def input_float(prompt, min_value=None):
    while True:
        try:
            v = float(input(prompt))
            if min_value is not None and v < min_value:
                print(f"Masukkan angka >= {min_value}")
                continue
            return v
        except:
            print("Input harus berupa angka!")

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ================== LOAD / SAVE JSON ==================
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ================== DATA ==================
inventory = load_json(INVENTORY_FILE, [])
borrows = load_json(BORROWS_FILE, [])
history = load_json(HISTORY_FILE, [])
employees = load_json(EMPLOYEES_FILE, [
    {"nama": "Rudi"},
    {"nama": "Siti"},
    {"nama": "Budi"},
    {"nama": "Rina"},
    {"nama": "Andi"}
])


# ================== HELPERS ==================
def find_item(kode):
    for i in inventory:
        if i["kode"] == kode:
            return i
    return None

def find_karyawan(nama):
    for k in employees:
        if k["nama"].lower() == nama.lower():
            return k
    return None

def record(action, detail):
    history.append({
        "waktu": now_str(),
        "aksi": action,
        "detail": detail
    })
    save_json(HISTORY_FILE, history)


# ================== LOGIN ADMIN ==================
def admin_login():
    print("\n=== LOGIN ===")
    username = input_nonempty("Username: ")
    
    if username not in ADMINS:
        print("Bukan admin!")
        return None
    
    pwd = getpass("Password: ")
    if pwd != ADMINS[username]:
        print("Password salah!")
        return None
    
    print(f"Login berhasil. Selamat datang, {username}")
    return username


# ================== CRUD BARANG ==================
def generate_kode_barang(kategori_prefix):
    nomor_tertinggi = 0
    for item in inventory:
        if item["kode"].startswith(kategori_prefix):
            try:
                nomor = int(item["kode"][1:])
                if nomor > nomor_tertinggi:
                    nomor_tertinggi = nomor
            except:
                pass
    
    # nomor baru
    nomor_baru = nomor_tertinggi + 1
    return f"{kategori_prefix}{nomor_baru:03d}"


# Tambah Barang
def tambah_barang(admin):
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== TAMBAH BARANG ===")

    print("Pilih kategori barang:")
    print("1. Elektronik")
    print("2. Furnitur")
    print("3. Kendaraan")
    print("4. Lainnya")

    pilih = input_nonempty("Pilih kategori (1-5): ")

    kategori_map = {
        "1": ("Elektronik", "E"),
        "2": ("Furnitur", "F"),
        "3": ("Kendaraan", "K"),
        "4": ("Lainnya", "L"),
    }

    if pilih not in kategori_map:
        print("Kategori tidak valid!")
        return

    kategori_nama, prefix = kategori_map[pilih]

    kode = generate_kode_barang(prefix)

    nama = input_nonempty("Nama barang: ")

    for brg in inventory:
        if brg["nama"].lower() == nama.lower():
            print("Nama barang sudah ada! Gunakan nama lain.")
            return

    stok = input_int("Stok awal: ", 0)
    harga = input_float("Harga: ", 0)

    item = {
        "kode": kode,
        "nama": nama,
        "kategori": kategori_nama,
        "stok": stok,
        "harga": harga
    }

    inventory.append(item)
    save_json(INVENTORY_FILE, inventory)
    record("tambah_barang", item)

    print(f"Barang '{nama}' berhasil ditambahkan dengan kode {kode}!")


# Lihat Barang
def lihat_barang(sort_by=None):

    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== DAFTAR BARANG ===")

    if not inventory:
        print("Belum ada barang.")
        return

    items = inventory[:]

    if sort_by == "a-z":
        items.sort(key=lambda x: x["nama"].lower())
    elif sort_by == "kategori":
        items.sort(key=lambda x: x["kategori"].lower())
    elif sort_by == "stok-desc":
        items.sort(key=lambda x: x["stok"], reverse=True)
    elif sort_by == "harga-desc":
        items.sort(key=lambda x: x["harga"], reverse=True)

    print(f"{'Kode':<8} {'Nama':<20} {'Kategori':<15} {'Stok':<5} {'Harga':<10}")
    print("-" * 65)

    for b in items:
        print(f"{b['kode']:<8} {b['nama']:<20} {b['kategori']:<15} "
          f"{b['stok']:<5} Rp {b['harga']:,.2f}")



# Ubah Barang
def ubah_barang(admin):

    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== DAFTAR BARANG ===")

    if not inventory:
        print("Tidak ada barang dalam inventaris!")
        return

    print(f"{'Kode':<8} {'Nama':<20} {'Kategori':<15} {'Stok':<5} {'Harga':<10}")
    print("-" * 65)

    for b in inventory:
        print(f"{b['kode']:<8} {b['nama']:<20} {b['kategori']:<15} {b['stok']:<5} {b['harga']:,.2f}")

    kode = input_nonempty("\nMasukkan kode barang yang mau diubah: ").upper()
    item = find_item(kode)

    if not item:
        print("Barang tidak ditemukan!")
        return

    print("\n=== DATA BARANG SAAT INI ===")
    print(f"Kode     : {item['kode']}")
    print(f"Nama     : {item['nama']}")
    print(f"Kategori : {item['kategori']}")
    print(f"Stok     : {item['stok']}")
    print(f"Harga    : Rp{item['harga']:,.2f}")
    print("=================================")
    print("Biarkan kosong jika tidak ingin mengubah.\n")

    nama = input("Nama baru     : ")
    kategori = input("Kategori baru : ")
    stok = input("Stok baru     : ")
    harga = input("Harga baru    : ")

    old = item.copy()

    if nama:
        item["nama"] = nama
    if kategori:
        item["kategori"] = kategori
    if stok.isdigit():
        item["stok"] = int(stok)
    if harga:
        try:
            item["harga"] = float(harga)
        except:
            print("Harga tidak valid.")

    save_json(INVENTORY_FILE, inventory)
    record("ubah_barang", {"sebelum": old, "sesudah": item})

    print("\nBarang berhasil diubah!")


# Hapus Barang
def hapus_barang(admin):
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== HAPUS BARANG ===")

    if not inventory:
        print("Tidak ada barang dalam inventaris.")
        return

    print("\n=== DAFTAR BARANG ===")
    print(f"{'Kode':<8} {'Nama':<20} {'Kategori':<15} {'Stok':<5} {'Harga':<10}")
    print("-" * 65)

    for b in inventory:
        print(f"{b['kode']:<8} {b['nama']:<20} {b['kategori']:<15} {b['stok']:<5} {b['harga']:,.2f}")

    print("-" * 65)

    kode = input_nonempty("Masukkan kode barang yang ingin dihapus: ").upper()
    item = find_item(kode)

    if not item:
        print("Barang dengan kode tersebut tidak ditemukan!")
        return

    print("\nAnda akan menghapus:")
    print(f"Kode     : {item['kode']}")
    print(f"Nama     : {item['nama']}")
    print(f"Kategori : {item['kategori']}")
    print(f"Stok     : {item['stok']}")
    print(f"Harga    : Rp{item['harga']:,.2f}")

    yakin = input("Yakin ingin menghapus? (y/n): ").lower()

    if yakin != "y":
        print("Penghapusan dibatalkan.")
        return

    inventory.remove(item)
    save_json(INVENTORY_FILE, inventory)
    record("hapus_barang", item)

    print(f"Barang '{item['nama']}' berhasil dihapus!")


# Peminjaman Barang
def pinjam_barang(admin):
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== PENCATATAN PEMINJAMAN ===")

    print("\nPeminjam:")
    print("1. Karyawan")
    print("2. Bukan karyawan")

    pil = input_nonempty("Pilih (1/2): ")

    if pil == "1":
        print("\n=== DAFTAR KARYAWAN ===")
        for idx, k in enumerate(employees, start=1):
            print(f"{idx}. {k['nama']}")

        pilih_karyawan = input_int("Pilih nomor karyawan: ", 1)
        
        if pilih_karyawan > len(employees):
            print("Nomor karyawan tidak valid!")
            return

        peminjam = employees[pilih_karyawan - 1]["nama"]
        is_karyawan = peminjam

    else:
        peminjam = input_nonempty("Nama peminjam: ")
        is_karyawan = "Bukan karyawan"

    # CARI BARANG BERDASARKAN NAMA
    nama_barang = input_nonempty("Nama barang: ").lower()

    item = None
    for brg in inventory:
        if brg["nama"].lower() == nama_barang:
            item = brg
            break

    if not item:
        print("Barang tidak ditemukan!")
        return

    # VALIDASI STOK
    if item["stok"] <= 0:
        print("Stok HABIS!")
        return

    qty = input_int("Jumlah dipinjam: ", 1)

    if qty > item["stok"]:
        print("Jumlah melebihi stok!")
        return

    days = input_int("Lama pinjam (hari): ", 1)

    now = datetime.now()
    due = now + timedelta(days=days)

    rec = {
        "id": f"PB{len(borrows)+1:03d}",
        "peminjam": peminjam,
        "karyawan": is_karyawan,
        "kode": item["kode"],
        "nama_barang": item["nama"],
        "qty": qty,
        "pinjam": now_str(),
        "jatuh_tempo": due.strftime("%Y-%m-%d %H:%M:%S"),
        "kembali": None,
        "status": "dipinjam",
        "denda": 0
    }

    borrows.append(rec)
    item["stok"] -= qty

    save_json(INVENTORY_FILE, inventory)
    save_json(BORROWS_FILE, borrows)
    record("pinjam", rec)

    print(f"Peminjaman dicatat! ID: {rec['id']}")


# Pengembalian Barang
from math import ceil

def pengembalian(admin):
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== PENGEMBALIAN BARANG ===")

    aktif = [r for r in borrows if r["status"] == "dipinjam"]

    if not aktif:
        print("Tidak ada peminjaman aktif!")
        return

    print(f"{'ID':<8} {'Peminjam':<15} {'Barang':<20} {'Qty':<5} {'Pinjam':<20} {'Jatuh Tempo':<20}")
    print("-" * 95)

    for r in aktif:
        print(
            f"{r['id']:<8} {r['peminjam']:<15} {r['nama_barang']:<20} "
            f"{r['qty']:<5} {r['pinjam']:<20} {r['jatuh_tempo']:<20}"
        )

    idb = input_nonempty("\nMasukkan ID Peminjaman yang mau dikembalikan: ").upper()

    rec = next((r for r in borrows if r["id"] == idb), None)

    if not rec:
        print("Data peminjaman tidak ditemukan!")
        return

    if rec["status"] != "dipinjam":
        print("Barang sudah pernah dikembalikan!")
        return

    item = find_item(rec["kode"])
    kembali_time = datetime.now()

    due = datetime.strptime(rec["jatuh_tempo"], "%Y-%m-%d %H:%M:%S")
    diff = kembali_time - due
    late_days = ceil(diff.total_seconds() / 86400) if diff.total_seconds() > 0 else 0
    denda_late = late_days * (item["harga"] * 0.05)

    qty = rec["qty"]
    print(f"\nBarang dipinjam sebanyak: {qty}")

    denda_kondisi = 0
    status = "dikembalikan"

    if qty == 1:
        print("\nKondisi barang:")
        print("1. Baik")
        print("2. Rusak (bisa diperbaiki)")
        print("3. Rusak (tidak bisa diperbaiki)")
        print("4. Hilang")

        kondisi = input_nonempty("Pilih (1-4): ")

        if kondisi == "1":
            item["stok"] += 1
            baik = 1
            rusak_ringan = 0
            rusak_berat = 0
            hilang = 0

        elif kondisi == "2":
            denda_kondisi = item["harga"] * 0.5
            baik = 0
            rusak_ringan = 1
            rusak_berat = 0
            hilang = 0

        elif kondisi == "3":
            denda_kondisi = item["harga"] * 0.75
            baik = 0
            rusak_ringan = 0
            rusak_berat = 1
            hilang = 0

        elif kondisi == "4":
            denda_kondisi = item["harga"]
            baik = 0
            rusak_ringan = 0
            rusak_berat = 0
            hilang = 1

        else:
            print("Input tidak valid!")
            return

    else:
        print("\nMasukkan jumlah kondisi barang:")
        baik = int(input("Jumlah BAIK                     : ") or 0)
        rusak_ringan = int(input("Jumlah RUSAK (bisa diperbaiki)  : ") or 0)
        rusak_berat  = int(input("Jumlah RUSAK (tidak bisa dibaiki): ") or 0)
        hilang = int(input("Jumlah HILANG                   : ") or 0)

        total = baik + rusak_ringan + rusak_berat + hilang

        if total != qty:
            print("\nTotal kondisi tidak sesuai jumlah barang yang dipinjam!")
            return

        # hitung denda kondisi
        denda_kondisi += rusak_ringan * (item["harga"] * 0.5)
        denda_kondisi += rusak_berat  * (item["harga"] * 0.75)
        denda_kondisi += hilang       * (item["harga"] * 1)

        # stok bertambah hanya dari barang baik
        item["stok"] += baik

    total_denda = denda_late + denda_kondisi

    rec["kembali"] = kembali_time.strftime("%Y-%m-%d %H:%M:%S")
    rec["status"] = status
    rec["denda"] = total_denda

    rec["detail_pengembalian"] = {
        "baik": baik,
        "rusak_bisa_diperbaiki": rusak_ringan,
        "rusak_tidak_bisa_diperbaiki": rusak_berat,
        "hilang": hilang
    }

    save_json(INVENTORY_FILE, inventory)
    save_json(BORROWS_FILE, borrows)
    record("kembali", rec)

    print("\n=== Rincian Pengembalian ===")
    print(f"Baik                        : {baik}")
    print(f"Rusak (bisa diperbaiki)     : {rusak_ringan}")
    print(f"Rusak (tidak bisa diperb.)  : {rusak_berat}")
    print(f"Hilang                      : {hilang}")

    print(f"\nTerlambat     : {late_days} hari")
    print(f"Denda telat   : Rp {denda_late:,.2f}")
    print(f"Denda kondisi : Rp {denda_kondisi:,.2f}")
    print(f"Total Denda   : Rp {total_denda:,.2f}")


# Cari Barang
def menu_cari_barang():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== CARI BARANG BERDASARKAN NAMA ===")
    kata = input_nonempty("Masukkan nama barang yang dicari: ").lower()

    hasil = [b for b in inventory if kata in b["nama"].lower()]

    if not hasil:
        print("Tidak ada barang yang cocok.")
        return

    print(f"\n{'Kode':<8} {'Nama':<20} {'Kategori':<15} {'Stok':<5} {'Harga':<10}")
    print("-" * 65)

    for b in hasil:
        print(f"{b['kode']:<8} {b['nama']:<20} {b['kategori']:<15} {b['stok']:<5} {b['harga']:,.2f}")


# Sorting Barang
def menu_sorting():
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        print("\n=== SORTING DATA BARANG ===")
        print("1. Urutkan Nama A - Z")
        print("2. Urutkan Berdasarkan Kategori")
        print("3. Stok Terbanyak ke Terkecil")
        print("4. Harga Termahal ke Termurah")
        print("5. Kembali")

        pilih = input("Pilih menu: ")

        if pilih == "1":
            lihat_barang(sort_by="a-z")
        elif pilih == "2":
            lihat_barang(sort_by="kategori")
        elif pilih == "3":
            lihat_barang(sort_by="stok-desc")
        elif pilih == "4":
            lihat_barang(sort_by="harga-desc")
        elif pilih == "5":
            break
        else:
            print("Pilihan tidak valid!")


# Laporan Aktif Barang yang Dipinjam
def laporan_aktif():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== PEMINJAMAN AKTIF ===\n")

    aktif = [r for r in borrows if r["status"] == "dipinjam"]

    if not aktif:
        print("Tidak ada peminjaman aktif.")
        return

    print(f"{'ID':<8} {'Peminjam':<15} {'Barang':<20} {'Qty':<5} {'Pinjam':<20} {'Jatuh Tempo':<20}")
    print("-" * 95)

    for r in aktif:
        print(f"{r['id']:<8} {r['peminjam']:<15} {r['nama_barang']:<20} "
              f"{r['qty']:<5} {r['pinjam']:<20} {r['jatuh_tempo']:<20}")


# Riwayat Aktivitas
def laporan_history():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== RIWAYAT AKTIVITAS (30 terakhir) ===\n")

    if not history:
        print("Belum ada riwayat.")
        return

    print(f"{'Waktu':<20} {'Aksi':<20} {'Detail':<40}")
    print("-" * 85)

    for h in history[-30:]:
        waktu = h.get("waktu", "-")
        aksi = h.get("aksi", "-")

        detail = str(h.get("detail", ""))
        if len(detail) > 38:
            detail = detail[:38] + "..."

        print(f"{waktu:<20} {aksi:<20} {detail:<40}")


# Barang Paling Sering Dipinjam
def laporan_popular():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== BARANG SERING DIPINJAM ===")

    if not borrows:
        print("Belum ada data peminjaman!")
        return

    # Hitung total peminjaman per kode barang
    hitung = {}
    for r in borrows:
        hitung[r["kode"]] = hitung.get(r["kode"], 0) + r["qty"]

    # Urutkan berdasarkan jumlah peminjaman terbanyak
    ranking = sorted(hitung.items(), key=lambda x: x[1], reverse=True)

    # Tampilkan 10 besar
    for kode, total in ranking[:10]:
        it = find_item(kode)

        if it is None:
            print(f"{kode} - (DATA BARANG TELAH DIHAPUS) dipinjam {total}x")
            continue

        print(f"{kode} - {it['nama']} dipinjam {total}x")


def menu_barang_bermasalah():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n=== DAFTAR BARANG BERMASALAH ===")

    masalah = []

    for r in borrows:
        det = r.get("detail_pengembalian")
        has_problem = False

        if det:
            if (
                det.get("rusak_bisa_diperbaiki", 0) > 0
                or det.get("rusak_tidak_bisa_diperbaiki", 0) > 0
                or det.get("hilang", 0) > 0
            ):
                has_problem = True

        else:
            status = r.get("status", "")
            if status in ("hilang", "rusak_bisa_diperbaiki", "rusak_tidak_bisa_diperbaiki"):
                has_problem = True

        if has_problem:
            masalah.append(r)

    if not masalah:
        print("Tidak ada barang bermasalah.")
        return

    print(f"{'ID':<8} {'Nama Barang':<20} {'Peminjam':<15} {'Baik':<5} {'R.Ringan':<8} {'R.Berat':<8} {'Hilang':<6} {'Tgl Kembali':<20} {'Catatan':<15}")
    print("-" * 125)

    for r in masalah:
        det = r.get("detail_pengembalian", {})
        baik = det.get("baik", 0)
        rusak_ringan = det.get("rusak_bisa_diperbaiki", 0)
        rusak_berat = det.get("rusak_tidak_bisa_diperbaiki", 0)
        hilang = det.get("hilang", 0)

        if not det:
            st = r.get("status", "")
            q = r.get("qty", 1)
            if st == "hilang":
                hilang = q
                baik = 0
            elif st == "rusak_bisa_diperbaiki":
                rusak_ringan = q
                baik = 0
            elif st == "rusak_tidak_bisa_diperbaiki":
                rusak_berat = q
                baik = 0
            else:
                baik = q

        tanggal = r.get("kembali", "-")
        catatan = r.get("status", "")

        print(
            f"{r['id']:<8} {r['nama_barang']:<20} {r['peminjam']:<15} "
            f"{baik:<5} {rusak_ringan:<8} {rusak_berat:<8} {hilang:<6} {tanggal:<20} {catatan:<15}"
        )


# ================== MENU ADMIN ==================
def menu_admin(admin):
    while True:
        print(f"\n=== MENU UTAMA ({admin}) ===")
        print("1. Tambah barang")
        print("2. Lihat barang")
        print("3. Ubah barang")
        print("4. Hapus barang")
        print("5. Catat peminjaman")
        print("6. Catat pengembalian")
        print("7. Cari barang")
        print("8. Sorting data barang")
        print("9. Laporan peminjaman aktif")
        print("10. Riwayat aktivitas")
        print("11. Barang paling sering dipinjam")
        print("12. Barang Bermasalah")
        print("13. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1": tambah_barang(admin)
        elif pilihan == "2": lihat_barang()
        elif pilihan == "3": ubah_barang(admin)
        elif pilihan == "4": hapus_barang(admin)
        elif pilihan == "5": pinjam_barang(admin)
        elif pilihan == "6": pengembalian(admin)
        elif pilihan == "7": menu_cari_barang()
        elif pilihan == "8": menu_sorting()
        elif pilihan == "9": laporan_aktif()
        elif pilihan == "10": laporan_history()
        elif pilihan == "11": laporan_popular()
        elif pilihan == "12": menu_barang_bermasalah()
        elif pilihan == "13": break
        else:
            print("Pilihan tidak valid!")


# ================== MAIN ==================
def main():
    print("=== INVENTARIS BARANG ===")
    admin = None

    while not admin:
        admin = admin_login()

    menu_admin(admin)
    print("Keluar. Terima kasih!")


if __name__ == "__main__":
    save_json(INVENTORY_FILE, inventory)
    save_json(BORROWS_FILE, borrows)
    save_json(HISTORY_FILE, history)
    save_json(EMPLOYEES_FILE, employees)
    main()