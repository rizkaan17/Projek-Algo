import psycopg2
import pandas as pd
from tabulate import tabulate
import getpass
from datetime import datetime
import os
import sys
import time
import questionary
import pyfiglet

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    class _CFallback:
        def __getattr__(self, name):
            return ""
    Fore = Style = _CFallback()

def clear_screen():
    """Clear console screen cross-platform."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def banner():
    ascii_art = pyfiglet.figlet_format("AGROMAME", font="big_money-ne", width=100, justify="center")
    print(Fore.GREEN + ascii_art)

def spinner(seconds=0.8, message="Processing"):
    chars = "|/-\\"
    end = time.time() + seconds
    sys.stdout.write(f"{Fore.YELLOW}{message}... {Style.RESET_ALL}")
    sys.stdout.flush()
    i = 0
    while time.time() < end:
        sys.stdout.write(chars[i % len(chars)])
        sys.stdout.flush()
        time.sleep(0.06)
        sys.stdout.write("\b")
        i += 1
    sys.stdout.write(" \n")

def prompt_enter():
    input(Fore.CYAN + "\nTekan Enter untuk melanjutkan..." + Style.RESET_ALL)

def safe_int(prompt, default=None, allowed=None):
    """Safe integer input with optional allowed list and default."""
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            n = int(val)
            if allowed and n not in allowed:
                print(Fore.RED + f"Pilihan tidak valid. Pilih: {allowed}" + Style.RESET_ALL)
                continue
            return n
        except ValueError:
            print(Fore.RED + "Input harus berupa angka. Coba lagi." + Style.RESET_ALL)

def confirm(prompt="Yakin? (y/n): "):
    while True:
        c = input(prompt).strip().lower()
        if c in ("y", "yes"):
            return True
        if c in ("n", "no"):
            return False
        print("Ketik 'y' atau 'n'.")

# ----------------- Database -----------------
def connectDB():
    """
    Tetap menggunakan connectDB() sesuai permintaan.
    Mengembalikan conn, cur jika sukses. Jika gagal, mengembalikan (None, None).
    """
    try:
        conn = psycopg2.connect(host="localhost", user ="postgres", password="riz27", dbname="Projek Akhir")
        cur = conn.cursor()
        print(Fore.GREEN + "Database connected successfully" + Style.RESET_ALL)
        return conn, cur
    except Exception as e:
        print(Fore.RED + "Failed to connect to database" + Style.RESET_ALL)
        print(Fore.YELLOW + "Error detail:", e, Style.RESET_ALL)
        return None, None
    
# ----------------- Program utama & menu -----------------
def main():
    while True:
        clear_screen()
        banner()
        spinner(0.6, "Memuat menu")

        pilihan = questionary.select(
            "Pilih opsi:",
            choices=[
                "Register",
                "Login",
                "Keluar"
            ]
        ).ask()

        if pilihan == "Register":
            registerasi()
        elif pilihan == "Login":
            login()
        elif pilihan == "Keluar":
            print(Fore.MAGENTA + "Program selesai. Terima kasih!" + Style.RESET_ALL)
            break

# ----------------- Menu Awal -----------------
def registerasi():
    clear_screen()
    banner()
    print(Fore.CYAN + "==== Registrasi Pelanggan ====" + Style.RESET_ALL)
    nama_pelanggan= input("Masukkan nama pelanggan: ").strip()
    username_pelanggan = input("Masukkan username: ").strip()
    kata_sandi_pelanggan = getpass.getpass("Masukkan kata_sandi: ").strip()
    no_telp_pelanggan = input("Masukkan nomor telepon: ").strip()

    if not nama_pelanggan or not username_pelanggan or not kata_sandi_pelanggan:
        print(Fore.RED + "Nama/username/password tidak boleh kosong." + Style.RESET_ALL)
        prompt_enter()
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        # cek username unik
        cur.execute("SELECT 1 FROM pelanggan WHERE username_pelanggan = %s", (username_pelanggan,))
        if cur.fetchone():
            print(Fore.RED + "Username sudah dipakai. Pilih yang lain." + Style.RESET_ALL)
            conn.close(); cur.close()
            prompt_enter(); return

        query = """
            INSERT INTO pelanggan (nama_pelanggan, username_pelanggan, kata_sandi_pelanggan, no_telp_pelanggan)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (nama_pelanggan, username_pelanggan, kata_sandi_pelanggan, no_telp_pelanggan))
        conn.commit()
        print(Fore.GREEN + "Registrasi berhasil!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Gagal registrasi:", e, Style.RESET_ALL)
        if conn:
            conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    prompt_enter()

def login():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "==== Login ====" + Style.RESET_ALL)

        pilihan = questionary.select(
            "Pilih opsi:",
            choices=[
                "Karyawan",
                "Pelanggan",
                "Kembali"
            ]
        ).ask()

        if pilihan == "Karyawan":
            login_karyawan()
        elif pilihan == "Pelanggan":
            login_pelanggan()
        elif pilihan == "Kembali":
            return

def login_karyawan():
    clear_screen()
    banner()
    print(Fore.CYAN + "==== Login Karyawan ====" + Style.RESET_ALL)
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

    karyawan = cari_karyawan_di_database(username, password)

    if karyawan :
        nama_lengkap = karyawan['nama_karyawan']
        role = karyawan['role']

        log_karyawan = [
            ["Nama Lengkap", nama_lengkap],
            ["Username", username],
            ["Password",  "*" * len(password)],
            ["Role", role]
        ]
        print("\n=== Data Login Karyawan ===")
        print(tabulate(log_karyawan, headers=["Data", "Keterangan"], tablefmt="fancy_grid"))
        print(Fore.GREEN + f"\nSelamat datang {nama_lengkap}! Anda login sebagai {role}.\n" + Style.RESET_ALL)

        if role == 'Manajer Produksi':
            halaman_menu_manager_produksi()
        elif role == 'Admin Produksi':
            halaman_menu_admin_produksi()
        elif role == 'Admin Gudang':
            halaman_menu_admin_gudang()
        else:
            print(Fore.YELLOW + "Role tidak dikenali." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Login gagal. Username atau password salah." + Style.RESET_ALL)
    prompt_enter()

def cari_karyawan_di_database(username, password):
    conn, cur = connectDB()
    if not conn:
        return None
    try:
        query = """SELECT k.nama_karyawan, k.username_karyawan, k.kata_sandi_karyawan, j.nama_jabatan
                   FROM karyawan k
                   JOIN jabatan j ON k.id_jabatan = j.id_jabatan
                   WHERE k.username_karyawan = %s AND k.kata_sandi_karyawan = %s"""
        cur.execute(query, (username, password))
        result = cur.fetchone()
        if result:
            karyawan = {
                'nama_karyawan': result[0],
                'username': result[1],
                'password': result[2],
                'role': result[3]
            }
            return karyawan
        return None
    except Exception as e:
        print(Fore.RED + "Error saat cari karyawan:", e, Style.RESET_ALL)
        return None
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def login_pelanggan():
    clear_screen()
    banner()
    print(Fore.CYAN + "==== Login Pelanggan ====" + Style.RESET_ALL)
    username_pelanggan = input("Masukkan username: ").strip()
    kata_sandi_pelanggan = getpass.getpass("Masukkan kata_sandi: ").strip()

    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        query = """SELECT id_pelanggan, nama_pelanggan, username_pelanggan, kata_sandi_pelanggan
                   FROM pelanggan
                   WHERE username_pelanggan = %s AND kata_sandi_pelanggan = %s"""
        cur.execute(query, (username_pelanggan, kata_sandi_pelanggan))
        result = cur.fetchone()

        if result:
            nama_pelanggan = result[1]
            username = result[2]
            password = result[3]

            log_pelanggan = [
                    ["Nama Lengkap", nama_pelanggan],
                    ["Username", username],
                    ["Password", "*" * len(password)]
                ]
            print("\n=== Data Login Pelanggan ===")
            print(tabulate(log_pelanggan, headers=["Data", "Keterangan"], tablefmt="fancy_grid"))
            print(Fore.GREEN + f"\nSelamat datang {nama_pelanggan}! Anda berhasil login sebagai Pelanggan.\n" + Style.RESET_ALL)
            halaman_menu_pelanggan(id_pelanggan = result[0])
        else:
            print(Fore.RED + "Login gagal! Username atau kata sandi salah." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Error saat login pelanggan:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    prompt_enter()

# ----------------- Admin Produksi (menu & fungsi) -----------------
def halaman_menu_admin_produksi():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Halaman Menu Admin Produksi ===" + Style.RESET_ALL)

        pilihan_adp = questionary.select(
            "Pilih menu:",
            choices=[
                "Biodata",
                "Hasil Panen",
                "Produksi",
                "Logout"
            ]
        ).ask()

        if pilihan_adp == "Biodata":
            biodata()
        elif pilihan_adp == "Hasil Panen":
            hasil_panen()
        elif pilihan_adp == "Produksi":
            produksi()
        elif pilihan_adp == "Logout":
            if questionary.confirm("Yakin ingin logout?").ask():
                print("Logout...")
                spinner(0.4)
                return

        prompt_enter()

def biodata():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Menu Biodata Karyawan ===" + Style.RESET_ALL)

        pilihan_bio = questionary.select(
            "Pilih menu:",
            choices=[
                "Lihat Biodata",
                "Edit Biodata",
                "Kembali"
            ]
        ).ask()

        if pilihan_bio == "Lihat Biodata":
            lihat_biodata_karyawan()
        elif pilihan_bio == "Edit Biodata":
            edit_bio_karyawan()
        elif pilihan_bio == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def edit_bio_karyawan():
    clear_screen()
    print("=== Edit Biodata ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    username_karyawan = input("Masukkan username: ")

    try:
        query = "SELECT * FROM karyawan WHERE username_karyawan = %s"
        cur.execute(query, (username_karyawan,))
        result = cur.fetchone()

        if result:
            print("Masukkan data baru (tekan Enter untuk tidak mengubah):")

            nama_baru = input(f"Nama ({result[1]}): ") or result[1]
            username_baru = input(f"Username ({result[2]}): ") or result[2]
            kata_sandi_baru = input(f"Kata Sandi ({result[3]}): ") or result[3]
            no_telp_baru = input(f"No Telepon ({result[6]}): ") or result[6]

            update_q = """
                UPDATE karyawan
                SET nama_karyawan=%s, username_karyawan=%s, kata_sandi_karyawan=%s, no_telp=%s
                WHERE username_karyawan=%s
            """
            cur.execute(update_q, (nama_baru, username_baru, kata_sandi_baru, no_telp_baru, username_karyawan))
            conn.commit()

            print(Fore.GREEN + "Biodata berhasil diperbarui." + Style.RESET_ALL)
            lihat_biodata_karyawan()
        else:
            print(Fore.YELLOW + "Data biodata tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def lihat_biodata_karyawan():
    clear_screen()
    print("=== Lihat Biodata ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    username_karyawan = input("Masukkan username: ")
    try:
        query = "SELECT * FROM karyawan WHERE username_karyawan = %s"
        cur.execute(query, (username_karyawan,))
        result = cur.fetchone()

        if result:
            biodata = [
                ["Nama", result[1]],
                ["Username", result[2]],
                ["Kata Sandi", result[3]],
                ["Gender", "Perempuan" if result[4] else "Laki-laki"],
                ["Tgl Lahir", result[5]],
                ["No Telepon", result[6]],
                ["Tgl Bergabung", result[7]],
                ["Gaji", result[9]]
            ]
            print("\n=== Biodata Admin Gudang ===")
            print(tabulate(biodata, headers=["Data", "Keterangan"], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "Data biodata tidak ditemukan." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Error:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def hasil_panen():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Menu Hasil Panen ===" + Style.RESET_ALL)

        pilihan_hp = questionary.select(
            "Pilih menu:",
            choices=[
                "Input Hasil Panen",
                "Edit Hasil Panen",
                "Hapus Hasil Panen",
                "Lihat Laporan Hasil Panen",
                "Kembali"
            ]
        ).ask()

        if pilihan_hp == "Input Hasil Panen":
            input_hp()
        elif pilihan_hp == "Hapus Hasil Panen":
            hapus_hp()
        elif pilihan_hp == "Edit Hasil Panen":
            edit_hp()
        elif pilihan_hp == "Lihat Laporan Hasil Panen":
            lihat_laporan_hp()
        elif pilihan_hp == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def input_hp():
    clear_screen()
    lihat_laporan_hp()
    print("=== Input Hasil Panen ===")

    # Input jumlah panen
    hasil_panen_in = input("Masukkan jumlah hasil panen (kg) [Enter untuk batal]: ")
    if hasil_panen_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        hasil_panen = float(hasil_panen_in)
    except ValueError:
        print(Fore.RED + "Input harus angka." + Style.RESET_ALL)
        prompt_enter()
        return
    
    # Input tanggal panen
    tanggal_panen = input("Masukkan tanggal panen (YYYY-MM-DD) [Enter untuk batal]: ")
    if tanggal_panen.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    # Input nama karyawan
    nama_karyawan = input("Masukkan nama karyawan [Enter untuk batal]: ").strip().lower()
    if nama_karyawan == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

   # Tampilkan ringkasan data sebelum simpan
    print("\n--- Konfirmasi Data ---")
    print(f"Jumlah Panen : {hasil_panen} kg")
    print(f"Tanggal Panen: {tanggal_panen}")
    print(f"Nama Karyawan: {nama_karyawan}")
    konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print(Fore.YELLOW + "Input dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Cari id_karyawan berdasarkan nama
        cur.execute("SELECT id_karyawan FROM karyawan WHERE nama_karyawan = %s", (nama_karyawan,))
        result = cur.fetchone()

        if not result:
            print(Fore.RED + "Nama karyawan tidak ditemukan." + Style.RESET_ALL)
            conn.close()
            return

        id_karyawan = result[0]

        query = """
            INSERT INTO hasil_panen (jmlh_panen, tgl_panen, id_karyawan)
            VALUES (%s, %s, %s)
        """
        cur.execute(query, (hasil_panen, tanggal_panen, id_karyawan))
        conn.commit()
        print(Fore.GREEN + "Input hasil panen berhasil!" + Style.RESET_ALL)
        lihat_laporan_hp()

    except Exception as e:
        print(Fore.RED + "Gagal input:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def hapus_hp():
    clear_screen()
    lihat_laporan_hp()
    print("=== Hapus Hasil Panen ===")
    lihat_laporan_hp()
    id_hp = safe_int("Masukkan ID hasil panen yang akan dihapus: ", default=None)
    if not confirm("Yakin ingin menghapus hasil panen ini? (y/n): "):
        print("Batal menghapus."); prompt_enter(); return
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        query = "DELETE FROM hasil_panen WHERE id_hp = %s"
        cur.execute(query, (id_hp,))
        conn.commit()
        print(Fore.GREEN + "Hasil Panen berhasil dihapus." + Style.RESET_ALL)
        lihat_laporan_hp
    except Exception as e:
        print(Fore.RED + "Gagal hapus:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def edit_hp():
    clear_screen()
    lihat_laporan_hp()  
    print("=== Edit Hasil Panen ===")
    lihat_laporan_hp()

    # Input ID hasil panen
    id_hp_in = input("Masukkan ID hasil panen yang akan diedit [Enter untuk batal]: ")
    if id_hp_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        id_hp = int(id_hp_in)
    except ValueError:
        print(Fore.RED + "ID harus angka." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = "SELECT * FROM hasil_panen WHERE id_hp = %s"
        cur.execute(query, (id_hp,))
        result = cur.fetchone()

        if result:
            print("Masukkan data baru (Enter untuk tidak mengubah / batal jika kosong di awal):")

            tgl_panen_baru = input(f"Tanggal Panen ({result[1]}): ") or result[1]
            jmlh_panen_baru = input(f"Jumlah Panen ({result[2]}): ") or result[2]
            nama_karyawan = input(f"Nama Karyawan ({result[3]}) [Enter untuk batal]: ").strip().lower()
            if nama_karyawan == "":
                print(Fore.YELLOW + "Edit dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                return

            # Cari id_karyawan berdasarkan nama
            cur.execute("SELECT id_karyawan FROM karyawan WHERE LOWER(nama_karyawan) = LOWER(%s)", (nama_karyawan,))
            result_karyawan = cur.fetchone()

            if not result_karyawan:
                print(Fore.RED + "Nama karyawan tidak ditemukan." + Style.RESET_ALL)
                conn.close()
                return

            id_karyawan = result_karyawan[0]

            # Konfirmasi sebelum update
            print("\n--- Konfirmasi Data ---")
            print(f"Tanggal Panen : {tgl_panen_baru}")
            print(f"Jumlah Panen  : {jmlh_panen_baru}")
            print(f"Nama Karyawan : {nama_karyawan}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Edit dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                return

            update_query = """
                UPDATE hasil_panen
                SET tgl_panen = %s, jmlh_panen = %s, id_karyawan = %s
                WHERE id_hp = %s
            """
            cur.execute(update_query, (tgl_panen_baru, jmlh_panen_baru, id_karyawan, id_hp))
            conn.commit()
            print(Fore.GREEN + "Hasil Panen berhasil diperbarui." + Style.RESET_ALL)
            lihat_laporan_hp()
        else:
            print(Fore.YELLOW + "Data hasil panen tidak ditemukan." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Gagal edit:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def lihat_laporan_hp():
    clear_screen()
    print("=== Laporan Hasil Panen ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        query =  """
            SELECT hp.id_hp, hp.jmlh_panen, hp.tgl_panen, k.nama_karyawan
            FROM hasil_panen hp
            JOIN karyawan k ON hp.id_karyawan = k.id_karyawan
            ORDER BY hp.tgl_panen 
        """
        cur.execute(query)
        results = cur.fetchall()
        if not results:
            print(Fore.YELLOW + "Tidak ada data hasil panen." + Style.RESET_ALL)
        else:
            df = pd.DataFrame(results, columns=['ID Hasil Panen', 'Hasil Panen (kg)', 'Tanggal Panen', 'Nama Karyawan'])
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(Fore.RED + "Gagal mengambil laporan:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def produksi():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Menu Produksi ===" + Style.RESET_ALL)

        pilihan_prod = questionary.select(
            "Pilih menu:",
            choices=[
                "Input Produksi",
                "Edit Produksi",
                "Hapus Produksi",
                "Lihat Laporan Produksi",
                "Kembali"
            ]
        ).ask()

        if pilihan_prod == "Input Produksi":
            input_produksi()
        elif pilihan_prod == "Lihat Laporan Produksi":
            lihat_laporan_produksi()
        elif pilihan_prod == "Edit Produksi":
            edit_produksi()
        elif pilihan_prod == "Hapus Produksi":
            hapus_produksi()
        elif pilihan_prod == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def input_produksi():
    clear_screen()
    lihat_laporan_hp()
    print("=== Input Produksi ===")

    tanggal_produksi = input("Masukkan tanggal produksi (YYYY-MM-DD) [Enter untuk batal]: ")
    if tanggal_produksi.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    jumlah_produksi_in = input("Masukkan jumlah produksi (kg) [Enter untuk batal]: ")
    if jumlah_produksi_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        jumlah_produksi = float(jumlah_produksi_in)
    except ValueError:
        print(Fore.RED + "Input jumlah harus angka." + Style.RESET_ALL)
        prompt_enter()
        return

    id_hp_in = input("Masukkan ID hasil panen [Enter untuk batal]: ")
    if id_hp_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        id_hp = int(id_hp_in)
    except ValueError:
        print(Fore.RED + "ID hasil panen harus angka." + Style.RESET_ALL)
        return

    id_status_in = input("Masukkan ID status produksi (2. ditunda / 3. proses) [Enter untuk default=3]: ")
    if id_status_in.strip() == "":
        id_status_produksi = 3
    else:
        try:
            id_status_produksi = int(id_status_in)
            if id_status_produksi not in [2, 3]:
                print(Fore.RED + "Status produksi hanya boleh 2 atau 3." + Style.RESET_ALL)
                return
        except ValueError:
            print(Fore.RED + "Status produksi harus angka." + Style.RESET_ALL)
            return

    nama_karyawan = input("Masukkan nama karyawan [Enter untuk batal]: ").strip().lower()
    if nama_karyawan == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        cur.execute("SELECT id_karyawan FROM karyawan WHERE LOWER(nama_karyawan) = LOWER(%s)", (nama_karyawan,))
        result_karyawan = cur.fetchone()

        if not result_karyawan:
            print(Fore.RED + "Nama karyawan tidak ditemukan." + Style.RESET_ALL)
            conn.close()
            return

        id_karyawan = result_karyawan[0]

        print("\n--- Konfirmasi Data ---")
        print(f"Tanggal Produksi : {tanggal_produksi}")
        print(f"Jumlah Produksi  : {jumlah_produksi} kg")
        print(f"ID Hasil Panen   : {id_hp}")
        print(f"Status Produksi  : {id_status_produksi}")
        print(f"Nama Karyawan    : {nama_karyawan}")
        konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
        if konfirmasi != "y":
            print(Fore.YELLOW + "Input produksi dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
            return

        query = """
            INSERT INTO produksi (tgl_produksi, jmlh_produksi, id_karyawan, id_hp, id_status_produksi)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (tanggal_produksi, jumlah_produksi, id_karyawan, id_hp, id_status_produksi))

        if id_status_produksi == 1:
            update_hp = "UPDATE hasil_panen SET jmlh_panen = 0 WHERE id_hp = %s"
            cur.execute(update_hp, (id_hp,))
        else:
            update_hp = "UPDATE hasil_panen SET jmlh_panen = jmlh_panen - %s WHERE id_hp = %s"
            cur.execute(update_hp, (jumlah_produksi, id_hp))
        conn.commit()
        print(Fore.GREEN + "Input produksi berhasil!" + Style.RESET_ALL)
        lihat_laporan_produksi()

    except Exception as e:
        print(Fore.RED + "Gagal input produksi:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


def lihat_laporan_produksi():
    clear_screen()
    print("=== Laporan Produksi ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        query =  """
            SELECT p.id_produksi, p.tgl_produksi, p.tgl_selesai, p.jmlh_produksi,
                   k.nama_karyawan, hp.id_hp, hp.jmlh_panen, sp.nama_status
            FROM produksi p
            JOIN karyawan k ON p.id_karyawan = k.id_karyawan
            JOIN hasil_panen hp ON p.id_hp = hp.id_hp
            JOIN status_produksi sp ON p.id_status_produksi = sp.id_status_produksi
            ORDER BY p.tgl_produksi DESC
        """
        cur.execute(query)
        results = cur.fetchall()
        if not results:
            print(Fore.YELLOW + "Belum ada data produksi." + Style.RESET_ALL)
        else:
            df = pd.DataFrame(results, columns=['ID Produksi', 'Tanggal Produksi','Tanggal Selesai', 'Jumlah Produksi', 'Nama Karyawan', 'ID Hasil Panen', 'Jumlah Hasil Panen (kg)', 'Status Produksi' ])
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(Fore.RED + "Gagal mengambil laporan produksi:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def edit_produksi():
    clear_screen()
    lihat_laporan_produksi()
    print("=== Edit Produksi ===")

    id_produksi_in = input("Masukkan ID produksi yang akan diedit [Enter untuk batal]: ")
    if id_produksi_in.strip() == "":
        print(Fore.YELLOW + "Edit dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        id_produksi = int(id_produksi_in)
    except ValueError:
        print(Fore.RED + "ID produksi harus angka." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = "SELECT * FROM produksi WHERE id_produksi = %s"
        cur.execute(query, (id_produksi,))
        result = cur.fetchone()

        if result:
            print("Masukkan data baru (Enter untuk tidak mengubah):")

            tgl_produksi_baru = input(f"Tanggal Produksi ({result[1]}): ") or result[1]
            jmlh_produksi_baru = input(f"Jumlah Produksi ({result[3]}): ") or result[3]

            nama_karyawan_baru = input(f"Nama Karyawan ({result[4]}) [Enter untuk batal]: ").strip().lower()
            if nama_karyawan_baru == "":
                print(Fore.YELLOW + "Edit dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                return

            id_hp_in = input(f"ID Hasil Panen ({result[5]}): ")
            id_hp_baru = int(id_hp_in) if id_hp_in.strip() != "" else result[5]

            id_status_in = input(f"ID Status Produksi (1. Selesai/2. Ditunda/3. Proses) ({result[6]}): ")
            id_status_produksi_baru = int(id_status_in) if id_status_in.strip() != "" else result[6]

            cur.execute("SELECT id_karyawan FROM karyawan WHERE LOWER(nama_karyawan) = LOWER(%s)", (nama_karyawan_baru,))
            result_karyawan = cur.fetchone()

            if not result_karyawan:
                print(Fore.RED + "Nama karyawan tidak ditemukan." + Style.RESET_ALL)
                conn.close()
                return

            id_karyawan = result_karyawan[0]

            print("\n--- Konfirmasi Data ---")
            print(f"Tanggal Produksi : {tgl_produksi_baru}")
            print(f"Jumlah Produksi  : {jmlh_produksi_baru}")
            print(f"Nama Karyawan    : {nama_karyawan_baru}")
            print(f"ID Hasil Panen   : {id_hp_baru}")
            print(f"Status Produksi  : {id_status_produksi_baru}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Edit dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                return

            if id_status_produksi_baru == 1:
                update_query = """
                    UPDATE produksi
                    SET tgl_produksi = %s, jmlh_produksi = %s, id_karyawan = %s, id_hp = %s, 
                        id_status_produksi = %s, tgl_selesai = %s
                    WHERE id_produksi = %s
                """
                cur.execute(update_query, (
                    tgl_produksi_baru, jmlh_produksi_baru, id_karyawan, id_hp_baru,
                    id_status_produksi_baru, datetime.now().strftime("%Y-%m-%d"), id_produksi
                ))

                cur.execute("UPDATE hasil_panen SET jmlh_panen = 0 WHERE id_hp = %s", (id_hp_baru,))
            else:
                update_query = """
                    UPDATE produksi
                    SET tgl_produksi = %s, jmlh_produksi = %s, id_karyawan = %s, id_hp = %s, id_status_produksi = %s
                    WHERE id_produksi = %s
                """
                cur.execute(update_query, (
                    tgl_produksi_baru, jmlh_produksi_baru, id_karyawan, id_hp_baru,
                    id_status_produksi_baru, id_produksi
                ))

            conn.commit()
            print(Fore.GREEN + "Produksi berhasil diperbarui & stok hasil panen disesuaikan." + Style.RESET_ALL)
            lihat_laporan_produksi()
        else:
            print(Fore.YELLOW + "Data produksi tidak ditemukan." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Gagal edit produksi:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def hapus_produksi():
    clear_screen()
    lihat_laporan_produksi()
    print("=== Hapus Produksi ===")
    id_produksi = safe_int("Masukkan ID produksi yang akan dihapus: ", default=None)
    if not confirm("Yakin menghapus produksi ini? (y/n): "):
        print("Batal penghapusan."); prompt_enter(); return
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        cur.execute("DELETE FROM produksi WHERE id_produksi = %s", (id_produksi,))
        conn.commit()
        print(Fore.GREEN + "Produksi berhasil dihapus." + Style.RESET_ALL)
        lihat_laporan_produksi()
    except Exception as e:
        print(Fore.RED + "Gagal menghapus produksi:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def halaman_menu_admin_gudang():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Halaman Menu Admin Gudang ===" + Style.RESET_ALL)

        pilihan_adg = questionary.select(
            "Pilih menu:",
            choices=[
                "Biodata",
                "Produk",
                "Transaksi",
                "Logout"
            ]
        ).ask()

        if pilihan_adg == "Biodata":
            biodata()
        elif pilihan_adg == "Produk":
            produk()
        elif pilihan_adg == "Transaksi":
            transaksi()
        elif pilihan_adg == "Logout":
            if questionary.confirm("Yakin ingin logout?").ask():
                print("Logout...")
                spinner(0.4)
                return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def produk():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Menu Produk ===" + Style.RESET_ALL)

        pilihan_prod = questionary.select(
            "Pilih menu:",
            choices=[
                "Input Produk",
                "Edit Produk",
                "Hapus Produk",
                "Lihat Laporan Produk",
                "Kembali"
            ]
        ).ask()

        if pilihan_prod == "Input Produk":
            input_produk()
        elif pilihan_prod == "Lihat Laporan Produk":
            lihat_laporan_produk()
        elif pilihan_prod == "Edit Produk":
            edit_produk()
        elif pilihan_prod == "Hapus Produk":
            hapus_produk()
        elif pilihan_prod == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def input_produk():
    clear_screen()
    lihat_laporan_produksi()
    print("=== Input Produk ===")
    jumlah_dibutuhkan = safe_int("Masukkan jumlah stok: ", default=None)
    id_jenis_produk = safe_int("Masukkan id jenis (1.Fresh, 2.Frozen, 3.Jus): ",
                               default=None, allowed=[1, 2, 3])

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Ambil produksi yang masih ada stok
        query = """
            SELECT id_produksi, jmlh_produksi
            FROM produksi
            WHERE jmlh_produksi > 0
            ORDER BY tgl_produksi ASC
        """
        cur.execute(query)
        produksis = cur.fetchall()

        sisa = jumlah_dibutuhkan
        total_diambil = 0
        id_produksi_terpakai = []

        # Kurangi stok produksi sesuai kebutuhan
        for id_produksi, jmlh_produksi in produksis:
            if sisa <= 0:
                break
            if jmlh_produksi >= sisa:
                cur.execute("""
                    UPDATE produksi
                    SET jmlh_produksi = jmlh_produksi - %s
                    WHERE id_produksi = %s
                """, (sisa, id_produksi))
                total_diambil += sisa
                id_produksi_terpakai.append(id_produksi)
                sisa = 0
            else:
                cur.execute("""
                    UPDATE produksi
                    SET jmlh_produksi = 0
                    WHERE id_produksi = %s
                """, (id_produksi,))
                total_diambil += jmlh_produksi
                id_produksi_terpakai.append(id_produksi)
                sisa -= jmlh_produksi

        # Jika stok cukup, masukkan ke tabel produk
        if sisa == 0:
            cur.execute("""
                INSERT INTO produk (stok, id_jenis_produk, tgl_update_stok)
                VALUES (%s, %s, NOW())
            """, (jumlah_dibutuhkan, id_jenis_produk))

            print(Fore.GREEN + "Input produk berhasil! Jumlah produksi berkurang dan produk tercatat." + Style.RESET_ALL)
            lihat_laporan_produk()
        else:
            print(Fore.YELLOW + "Stok habis! Tidak bisa memenuhi semua permintaan." + Style.RESET_ALL)

        conn.commit()

    except Exception as e:
        print(Fore.RED + "Gagal input produk:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def lihat_laporan_produk():
    clear_screen()
    print("=== Laporan Produk ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        query = """
            SELECT p.id_produk, j.nama_jenis, p.stok, p.tgl_update_stok, ps.jmlh_produksi
            FROM produk p
            JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
            LEFT JOIN produksi ps ON p.id_produksi = ps.id_produksi
        """
        cur.execute(query)
        results = cur.fetchall()
        if not results:
            print(Fore.YELLOW + "Belum ada produk tersedia." + Style.RESET_ALL)
        else:
            df = pd.DataFrame(results, columns=['ID Produk', 'Jenis Produk', 'Jumlah Produk', 'Tanggal Update Stok', 'Jumlah Produksi'])
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(Fore.RED + "Gagal:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def edit_produk():
    clear_screen()
    lihat_laporan_produk()
    print("=== Edit Produk ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return

    id_produk = safe_int("Masukkan ID produk yang akan diedit: ", default=None)
    if id_produk is None:
        print(Fore.YELLOW + "ID produk tidak valid." + Style.RESET_ALL)
        return

    try:
        cur.execute("SELECT * FROM produk WHERE id_produk = %s", (id_produk,))
        result = cur.fetchone()
        if result:
            stok_baru = input(f"Stok baru ({result[1]}), Enter untuk skip: ")
            
            if stok_baru.strip() == "":
                print(Fore.YELLOW + "Tidak ada perubahan stok." + Style.RESET_ALL)
            else:
                stok_baru = int(stok_baru)  # pastikan integer
                update_query = """
                    UPDATE produk
                    SET stok = %s, tgl_update_stok = %s
                    WHERE id_produk = %s
                """
                cur.execute(update_query, (stok_baru, datetime.now(), id_produk))
                conn.commit()
                print(Fore.GREEN + "Produk berhasil diperbarui." + Style.RESET_ALL)
            lihat_laporan_produk()
        else:
            print(Fore.YELLOW + "Data produk tidak ditemukan." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Gagal edit produk:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def hapus_produk():
    clear_screen()
    lihat_laporan_produk()
    print("=== Hapus Produk ===")
    id_produk = safe_int("Masukkan ID produk yang akan dihapus: ", default=None)
    if not confirm("Yakin menghapus produk ini? (y/n): "):
        print("Batal menghapus."); prompt_enter(); return
    conn, cur = connectDB()
    if not conn:
        prompt_enter(); return
    try:
        cur.execute("DELETE FROM produk WHERE id_produk=%s", (id_produk,))
        conn.commit()
        print(Fore.GREEN + "Produk berhasil dihapus." + Style.RESET_ALL)
        lihat_laporan_produk()
    except Exception as e:
        print(Fore.RED + "Gagal hapus produk:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def transaksi():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Menu Transaksi ===" + Style.RESET_ALL)
        pilihan_trans = questionary.select(
            "Pilih menu:",  
            choices=[
                "Lihat Laporan Transaksi",
                "Update Status Transaksi",
                "Kembali"
            ]
        ).ask()
        if pilihan_trans == "Update Status Transaksi":
            update_status_transaksi()   
        elif pilihan_trans == "Lihat Laporan Transaksi":
            lihat_laporan_transaksi()
        elif pilihan_trans == "Kembali":
            return  
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def update_status_transaksi():
    clear_screen()
    lihat_laporan_transaksi()
    print("=== Input Status Transaksi ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return
    id_transaksi = safe_int("Masukkan ID transaksi yang akan diperbarui: ", default=None)
    status_baru = safe_int("Masukkan status produksi baru (1. selesai/ 2. proses /3. dibatalkan): ", default=None, allowed=[1,2,3])
    try:
        query = """
            UPDATE transaksi
            SET id_status_transaksi = %s
            WHERE id_transaksi = %s
        """
        cur.execute(query, (status_baru, id_transaksi))
        conn.commit()
        print(Fore.GREEN + "Status transaksi berhasil diperbarui!" + Style.RESET_ALL)
        lihat_laporan_transaksi()
    except Exception as e:
        print(Fore.RED + "Gagal update status:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def lihat_laporan_transaksi():
    clear_screen()
    print("=== Laporan Transaksi ===")
    conn, cur = connectDB()
    if not conn:
        prompt_enter() 
        return
    try:
        query = """
            SELECT dt.id_detail_transaksi, t.id_transaksi, t.tgl_transaksi, jp.nama_jenis, dt.quantity, st.nama_status
            FROM transaksi t
            JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk p ON dt.id_produk = p.id_produk
            JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
            ORDER BY t.tgl_transaksi
        """
        cur.execute(query)
        results = cur.fetchall()
        if not results:
            print(Fore.YELLOW + "Belum ada transaksi." + Style.RESET_ALL)
        else:
            df = pd.DataFrame(results, columns=['ID Detail', 'ID Transaksi', 'Tanggal', 'Produk', 'Jumlah Produk', 'Status Transaksi'])
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(Fore.RED + "Gagal ambil laporan transaksi:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def halaman_menu_manager_produksi():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Halaman Menu Manager Produksi ===" + Style.RESET_ALL)

        pilihan_mng = questionary.select(
            "Pilih menu:",
            choices=[
                "Biodata",
                "Kelola akun karyawan",
                "Kelola transaksi pelanggan",
                "Pergantian manager produksi",
                "Kembali"
            ]
        ).ask()

        if pilihan_mng == "Biodata":
            biodata()
        elif pilihan_mng == "Kelola akun karyawan":
            kelola_akun_karyawan()
        elif pilihan_mng == "Kelola transaksi pelanggan":
            kelola_transaksi_pelanggan()
        elif pilihan_mng == "Pergantian manager produksi":
            ganti_mgr_baru()
        elif pilihan_mng == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def kelola_akun_karyawan():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Kelola Akun Karyawan ===" + Style.RESET_ALL)

        pilihan_akun = questionary.select(
            "Pilih menu:",
            choices=[
                "Tambah Karyawan",
                "Edit Karyawan",
                "Hapus Karyawan",
                "Lihat Laporan Karyawan",
                "Kembali"
            ]
        ).ask()

        if pilihan_akun == "Tambah Karyawan":
            tambah_karyawan()
        elif pilihan_akun == "Edit Karyawan":
            edit_karyawan()
        elif pilihan_akun == "Hapus Karyawan":
            hapus_karyawan()
        elif pilihan_akun == "Lihat Laporan Karyawan":
            lihat_karyawan()
        elif pilihan_akun == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL)

        prompt_enter()

def tambah_karyawan():
    clear_screen()
    print("=== Tambah Karyawan ===")

    nama = input("Nama [Enter untuk batal]: ")
    if nama.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    username = input("Username [Enter untuk batal]: ")
    if username.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    sandi = input("Password [Enter untuk batal]: ")
    if sandi.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    gender_in = input("Gender (1. Perempuan / 0. Laki-laki) [Enter untuk batal]: ")
    if gender_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        gender_input = int(gender_in)
        gender = True if gender_input == 1 else False
    except ValueError:
        print(Fore.RED + "Gender harus angka 1 atau 0." + Style.RESET_ALL)
        return

    status_in = input("Status (1. Aktif / 0. Nonaktif) [Enter untuk batal]: ")
    if status_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        status_input = int(status_in)
        status = True if status_input == 1 else False
    except ValueError:
        print(Fore.RED + "Status harus angka 1 atau 0." + Style.RESET_ALL)
        return

    tgl_lahir = input("Tanggal Lahir (YYYY-MM-DD) [Enter untuk batal]: ")
    if tgl_lahir.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    no_telp = input("No Telepon [Enter untuk batal]: ")
    if no_telp.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    id_jabatan_in = input("ID Jabatan (2. Admin Produksi / 3. Admin Gudang) [Enter untuk batal]: ")
    if id_jabatan_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        id_jabatan = int(id_jabatan_in)
    except ValueError:
        print(Fore.RED + "ID Jabatan harus angka." + Style.RESET_ALL)
        return

    gaji_in = input("Gaji [Enter untuk batal]: ")
    if gaji_in.strip() == "":
        print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        gaji = int(gaji_in)
    except ValueError:
        print(Fore.RED + "Gaji harus angka." + Style.RESET_ALL)
        return

    print("\n--- Konfirmasi Data ---")
    print(f"Nama       : {nama}")
    print(f"Username   : {username}")
    print(f"Password   : {sandi}")
    print(f"Gender     : {'Perempuan' if gender else 'Laki-laki'}")
    print(f"Status     : {'Aktif' if status else 'Nonaktif'}")
    print(f"Tgl Lahir  : {tgl_lahir}")
    print(f"No Telepon : {no_telp}")
    print(f"ID Jabatan : {id_jabatan}")
    print(f"Gaji       : {gaji}")
    konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print(Fore.YELLOW + "Input karyawan dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        cur.execute("""
            INSERT INTO karyawan 
            (nama_karyawan, username_karyawan, kata_sandi_karyawan, gender, status_karyawan, tgl_lahir, no_telp, tgl_masuk, id_jabatan, gaji_karyawan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nama, username, sandi, gender, status, tgl_lahir, no_telp, datetime.now().date(), id_jabatan, gaji))
        conn.commit()
        print(Fore.GREEN + "Karyawan berhasil ditambahkan." + Style.RESET_ALL)
        lihat_karyawan()
    except Exception as e:
        print(Fore.RED + "Gagal tambah karyawan:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def edit_karyawan():
    conn, cur = connectDB()
    if not conn: return
    id_karyawan = input("Masukkan ID Karyawan: ")
    cur.execute("SELECT * FROM karyawan WHERE id_karyawan = %s", (id_karyawan,))
    result = cur.fetchone()
    if result:
        print("Isi data baru (isi kembali jika tidak ingin mengubah):")
        nama_baru = input(f"Nama ({result[1]}): ") or result[1]
        username_baru = input(f"Username ({result[2]}): ") or result[2]
        sandi_baru = input(f"Password ({result[3]}): ") or result[3]
        gender_baru = int(input(f"Gender ({result[4]}) (1. Perempuan / 0. Laki-laki): "))
        gender = True if gender_baru == 1 else False
        status_baru = int(input(f"Status ({result[8]}) (1. Aktif / 0. Nonaktif): "))
        status = True if status_baru == 1 else False
        gaji_baru = int(input(f"Gaji ({result[9]}): ")) or result[9]
        jabatan_baru = input(f"ID Jabatan ({result[10]}) (2. Admin Produksi/ 3. Admin Gudang): ") or result[10]

        cur.execute("""
    UPDATE karyawan
    SET nama_karyawan = %s, username_karyawan = %s, kata_sandi_karyawan = %s, gender = %s, status_karyawan = %s,
        gaji_karyawan = %s, id_jabatan = %s
    WHERE id_karyawan = %s
    """, (nama_baru, username_baru, sandi_baru, gender, status, gaji_baru, jabatan_baru, id_karyawan))

        conn.commit()
        print("Data karyawan berhasil diperbarui.")
        lihat_karyawan()
    else:
        print("Karyawan tidak ditemukan.")
    cur.close(); conn.close()

def hapus_karyawan():
    conn, cur = connectDB()
    if not conn: return
    id_karyawan = input("Masukkan ID Karyawan: ")
    cur.execute("DELETE FROM karyawan WHERE id_karyawan = %s", (id_karyawan,))
    conn.commit()
    if cur.rowcount > 0:
        print("Karyawan berhasil dihapus.")
    else:
        print("Karyawan tidak ditemukan.")
    cur.close(); conn.close()

def hapus_karyawan():
    clear_screen()
    print("=== Hapus Karyawan ===")

    id_karyawan_in = input("Masukkan ID Karyawan [Enter untuk batal]: ")
    if id_karyawan_in.strip() == "":
        print(Fore.YELLOW + "Hapus dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
        return
    try:
        id_karyawan = int(id_karyawan_in)
    except ValueError:
        print(Fore.RED + "ID karyawan harus angka." + Style.RESET_ALL)
        return

    conn, cur = connectDB()
    if not conn: return

    try:
        cur.execute("SELECT nama_karyawan, username_karyawan FROM karyawan WHERE id_karyawan = %s", (id_karyawan,))
        result = cur.fetchone()
        if not result:
            print(Fore.YELLOW + "Karyawan tidak ditemukan." + Style.RESET_ALL)
            return

        print("\n--- Konfirmasi Hapus ---")
        print(f"Nama     : {result[0]}")
        print(f"Username : {result[1]}")
        konfirmasi = input("Apakah yakin ingin menghapus karyawan ini? (y/n): ").strip().lower()
        if konfirmasi != "y":
            print(Fore.YELLOW + "Hapus dibatalkan." + Style.RESET_ALL)
            return

        cur.execute("DELETE FROM karyawan WHERE id_karyawan = %s", (id_karyawan,))
        conn.commit()
        if cur.rowcount > 0:
            print(Fore.GREEN + "Karyawan berhasil dihapus." + Style.RESET_ALL)
            lihat_karyawan()
        else:
            print(Fore.YELLOW + "Karyawan tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal hapus karyawan:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def lihat_karyawan():
    clear_screen()
    print("=== Lihat Data Karyawan ===")

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return
    
    try:
        cur.execute("""
        SELECT k.id_karyawan, k.nama_karyawan, k.username_karyawan, k.kata_sandi_karyawan, k.gender, k.tgl_lahir,
        k.no_telp, k.tgl_masuk, k.status_karyawan, k.gaji_karyawan, j.nama_jabatan 
        FROM karyawan k
        JOIN jabatan j ON k.id_jabatan = j.id_jabatan
        ORDER BY k.id_karyawan
        """)
        data = cur.fetchall()
        
        if data:
            print(Fore.GREEN + "\n=== Daftar Karyawan ===" + Style.RESET_ALL)
            headers = ['Id Karyawan', 'Nama Karyawan', 'Username', 'Password', 'Gender', 'Tanggal Lahir',  'No Telepon', 'Tanggal Masuk',  'Status',  'Gaji', 'Jabatan']
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print(Fore.YELLOW + "Belum ada data karyawan." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + "Gagal menampilkan data:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def kelola_transaksi_pelanggan():
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== Kelola Transaksi Pelanggan ===" + Style.RESET_ALL)
        pilihan_transaksi = questionary.select(
            "Pilih menu:",
            choices=[
                "Lihat Laporan Transaksi",
                "Lihat Riwayat Transaksi",
                "Kembali"
            ]
        ).ask()
        if pilihan_transaksi == "Lihat Laporan Transaksi":
            lihat_transaksi()
        elif pilihan_transaksi == "Lihat Riwayat Transaksi":
            lihat_riwayat_transaksi()
        elif pilihan_transaksi == "Kembali":
            return
        else:
            print(Fore.RED + "Pilihan tidak valid, coba lagi." + Style.RESET_ALL) 

        prompt_enter()

def lihat_riwayat_transaksi():
    clear_screen()
    print("=== Lihat Riwayat Transaksi ===")

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = """
        SELECT 
            t.id_transaksi, t.tgl_transaksi, jp.nama_jenis AS jenis_produk, dt.quantity, jp.harga_produk,
            (dt.quantity * jp.harga_produk) AS subtotal, pl.nama_pelanggan, mp.nama_metode_pembayaran, st.nama_status
        FROM transaksi t
        JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
        JOIN produk p ON dt.id_produk = p.id_produk
        JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
        JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
        JOIN pelanggan pl ON t.id_pelanggan = pl.id_pelanggan
        JOIN metode_pembayaran mp ON t.id_metode_pembayaran = mp.id_metode_pembayaran
        WHERE st.nama_status = 'selesai'
        ORDER BY t.tgl_transaksi
        """
        cur.execute(query)
        data = cur.fetchall()

        if data:
            print(Fore.GREEN + "\n=== Daftar Riwayat Transaksi ===" + Style.RESET_ALL)
            headers = ["ID Transaksi", "Tanggal", "Jenis Produk", "Jumlah", 
                       "Harga Satuan", "Subtotal", "Nama Pelanggan", 
                       "Metode Pembayaran", "Status"]
            print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "Belum ada riwayat transaksi dengan status 'selesai'." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal menampilkan riwayat transaksi:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def lihat_transaksi():
    clear_screen()
    print("=== Lihat Transaksi ===")

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = """
            SELECT 
                t.id_transaksi, t.tgl_transaksi, jp.nama_jenis, dt.quantity, jp.harga_produk,
                (dt.quantity * jp.harga_produk) AS subtotal, st.nama_status
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk p ON dt.id_produk = p.id_produk
            JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
            JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
        """
        cur.execute(query)
        result = cur.fetchall()

        if result:
            print(Fore.GREEN + "\n=== Daftar Transaksi ===" + Style.RESET_ALL)
            headers = ['ID Transaksi', 'Tanggal', 'Jenis Produk',
                       'Jumlah', 'Harga Satuan', 'Subtotal', 'Status']
            print(tabulate(result, headers=headers, tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "Transaksi tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal menampilkan transaksi:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def ganti_mgr_baru():
    clear_screen()
    print("=== Ganti Manager Baru ===")

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        username_karyawan = input("Masukkan username manager lama [Enter untuk batal]: ")
        if username_karyawan.strip() == "":
            print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
            return

        query = "SELECT * FROM karyawan WHERE username_karyawan = %s"
        cur.execute(query, (username_karyawan,))
        result = cur.fetchone()

        if result:
            print("Masukkan data manager baru (Enter untuk batal):")

            nama_baru = input("Nama Manager Baru [Enter untuk batal]: ")
            if nama_baru.strip() == "":
                print(Fore.YELLOW + "Dibatalkan." + Style.RESET_ALL)
                return

            gender_in = input("Gender (1. Perempuan / 0. Laki-laki) [Enter untuk batal]: ")
            if gender_in.strip() == "":
                print(Fore.YELLOW + "Dibatalkan." + Style.RESET_ALL)
                return
            try:
                gender = int(gender_in)
                gender_baru = True if gender == 1 else False
            except ValueError:
                print(Fore.RED + "Gender harus angka 1 atau 0." + Style.RESET_ALL)
                return

            tgl_lahir_baru = input("Tgl Lahir (YYYY-MM-DD) [Enter untuk batal]: ")
            if tgl_lahir_baru.strip() == "":
                print(Fore.YELLOW + "Dibatalkan." + Style.RESET_ALL)
                return

            no_telp_baru = input("No Telepon [Enter untuk batal]: ")
            if no_telp_baru.strip() == "":
                print(Fore.YELLOW + "Dibatalkan." + Style.RESET_ALL)
                return

            tgl_masuk_baru = datetime.now().date()

            print("\n--- Konfirmasi Data ---")
            print(f"Nama Manager Baru : {nama_baru}")
            print(f"Gender            : {'Perempuan' if gender_baru else 'Laki-laki'}")
            print(f"Tgl Lahir         : {tgl_lahir_baru}")
            print(f"No Telepon        : {no_telp_baru}")
            print(f"Tgl Masuk         : {tgl_masuk_baru}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Update dibatalkan." + Style.RESET_ALL)
                return

            update_query = """
                UPDATE karyawan 
                SET nama_karyawan = %s, gender = %s, tgl_lahir = %s, no_telp = %s, tgl_masuk = %s
                WHERE username_karyawan = %s
            """
            cur.execute(update_query, (nama_baru, gender_baru, tgl_lahir_baru, no_telp_baru, tgl_masuk_baru, username_karyawan))
            conn.commit()
            print(Fore.GREEN + "Manager baru berhasil diganti. Tanggal masuk otomatis diisi hari ini." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Data manager tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal ganti manager:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def halaman_menu_pelanggan(id_pelanggan):
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== AGROMAME: Menu Utama Pembelian ===" + Style.RESET_ALL)

        pilihan = questionary.select(
            "Pilih menu:",
            choices=[
                "Biodata",
                "Belanja Produk",
                "Lihat Riwayat Transaksi Pembelian",
                "Logout"
            ]
        ).ask()

        if pilihan == "Biodata":
            biodata_pelanggan(id_pelanggan)
        elif pilihan == "Belanja Produk":
            belanja_produk(id_pelanggan)
        elif pilihan == "Lihat Riwayat Transaksi Pembelian":
            lihat_riwayat_transaksi_pembelian(id_pelanggan)
        elif pilihan == "Logout":
            print("Logout berhasil.")
            break
        else:
            print(Fore.RED + "Pilihan tidak valid!" + Style.RESET_ALL)

        prompt_enter()

def belanja_produk(id_pelanggan):
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== AGROMAME: Menu Belanja Produk ===" + Style.RESET_ALL)

        pilihan = questionary.select(
            "Pilih menu:",
            choices=[
                "Pilih Produk",
                "Lihat Keranjang",
                "Edit Keranjang",
                "Pilih Metode Pembayaran",
                "Edit Metode Pembayaran",
                "Checkout",
                "Kembali"
            ]
        ).ask()

        if pilihan == "Pilih Produk":
            pilih_produk(id_pelanggan)
        elif pilihan == "Lihat Keranjang":
            lihat_keranjang(id_pelanggan)
        elif pilihan == "Edit Keranjang":
            edit_keranjang(id_pelanggan)
        elif pilihan == "Pilih Metode Pembayaran":
            pilih_metode_pembayaran(id_pelanggan)
        elif pilihan == "Edit Metode Pembayaran":
            edit_metode_pembayaran(id_pelanggan)
        elif pilihan == "Checkout":
            checkout(id_pelanggan)
        elif pilihan == "Kembali":
            break
        else:
            print(Fore.RED + "Pilihan tidak valid!" + Style.RESET_ALL)
            prompt_enter()

def biodata_pelanggan(id_pelanggan):
    while True:
        clear_screen()
        banner()
        print(Fore.CYAN + "=== AGROMAME: Menu Biodata ===" + Style.RESET_ALL)

        pilihan = questionary.select(
            "Pilih menu:",
            choices=[
                "Lihat Biodata",
                "Edit Biodata",
                "Kembali"
            ]
        ).ask()

        if pilihan == "Lihat Biodata":
            lihat_biodata(id_pelanggan)
        elif pilihan == "Edit Biodata":
            edit_biodata(id_pelanggan)
        elif pilihan == "Kembali":
            break
        else:
            print(Fore.RED + "Pilihan tidak valid!" + Style.RESET_ALL)
            prompt_enter()  

def lihat_biodata(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Lihat Biodata Pelanggan ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = """
            SELECT p.nama_pelanggan, p.username_pelanggan, p.kata_sandi_pelanggan, p.no_telp_pelanggan,
                   a.nama_jalan, d.nama_desa, k.nama_kecamatan, kb.nama_kabupaten
            FROM pelanggan p
            LEFT JOIN alamat a ON p.id_alamat = a.id_alamat
            LEFT JOIN desa d ON a.id_desa = d.id_desa
            LEFT JOIN kecamatan k ON d.id_kecamatan = k.id_kecamatan
            LEFT JOIN kabupaten kb ON k.id_kabupaten = kb.id_kabupaten
            WHERE p.id_pelanggan = %s
        """
        cur.execute(query, (id_pelanggan,))
        data = cur.fetchone()

        if data:
            print(Fore.GREEN + "=== BIODATA ===" + Style.RESET_ALL)
            if data[4]:  # ada nama_jalan
                headers = ["Nama", "Username", "Kata Sandi", "No Telp", "Jalan", "Desa", "Kecamatan", "Kabupaten"]
                print(tabulate([data], headers=headers, tablefmt="fancy_grid"))
            else:  # alamat belum diisi
                headers = ["Nama", "Username", "Kata Sandi", "No Telp", "Alamat"]
                row = [data[0], data[1], data[2], data[3], "Belum diisi"]
                print(tabulate([row], headers=headers, tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "Data biodata pelanggan tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal menampilkan biodata:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def edit_biodata(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Edit Biodata ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = """
            SELECT p.nama_pelanggan, p.username_pelanggan, p.kata_sandi_pelanggan,
                   p.no_telp_pelanggan, a.id_alamat, a.nama_jalan, d.id_desa, d.nama_desa
            FROM pelanggan p
            LEFT JOIN alamat a ON p.id_alamat = a.id_alamat
            LEFT JOIN desa d ON a.id_desa = d.id_desa
            WHERE p.id_pelanggan = %s
        """
        cur.execute(query, (id_pelanggan,))
        data = cur.fetchone()

        if data:
            print("Isi data baru (Enter untuk tidak mengubah / batal jika kosong di awal):")

            nama = input(f"Nama ({data[0]}): ") or data[0]
            user = input(f"Username ({data[1]}): ") or data[1]
            sandi = input(f"Kata Sandi ({data[2]}): ") or data[2]
            telp = input(f"No Telp ({data[3]}): ") or data[3]

            if data[4]:  # alamat sudah ada
                jalan = input(f"Nama Jalan ({data[5]}): ") or data[5]
                desa = input(f"ID Desa ({data[6]} - {data[7]}): ") or data[6]

                cur.execute("""
                    UPDATE alamat SET nama_jalan = %s, id_desa = %s
                    WHERE id_alamat = %s
                """, (jalan, desa, data[4]))
            else:  # alamat belum ada
                print("Alamat belum ada, silakan isi:")
                jalan = input("Nama Jalan [Enter untuk batal]: ")
                if jalan.strip() == "":
                    print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
                    return
                desa = input("ID Desa [Enter untuk batal]: ")
                if desa.strip() == "":
                    print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
                    return

                cur.execute("""
                    INSERT INTO alamat (nama_jalan, id_desa)
                    VALUES (%s, %s) RETURNING id_alamat
                """, (jalan, desa))
                id_alamat_baru = cur.fetchone()[0]

                cur.execute("""
                    UPDATE pelanggan SET id_alamat = %s
                    WHERE id_pelanggan = %s
                """, (id_alamat_baru, id_pelanggan))

            # Konfirmasi sebelum update biodata
            print("\n--- Konfirmasi Data ---")
            print(f"Nama     : {nama}")
            print(f"Username : {user}")
            print(f"Kata Sandi: {sandi}")
            print(f"No Telp  : {telp}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
                return

            cur.execute("""
                UPDATE pelanggan
                SET nama_pelanggan = %s,
                    username_pelanggan = %s,
                    kata_sandi_pelanggan = %s,
                    no_telp_pelanggan = %s
                WHERE id_pelanggan = %s
            """, (nama, user, sandi, telp, id_pelanggan))

            conn.commit()
            print(Fore.GREEN + "Biodata berhasil diperbarui." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Data tidak ditemukan." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal edit biodata:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def pilih_produk(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Pilih Produk ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Ambil status 'proses'
        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'proses' tidak ada di status_transaksi." + Style.RESET_ALL)
            return
        id_status = s[0]

        # Cari transaksi aktif
        cur.execute("""
            SELECT t.id_transaksi
            FROM transaksi t
            WHERE t.id_pelanggan = %s AND t.id_status_transaksi = %s
            ORDER BY t.id_transaksi DESC
            LIMIT 1
        """, (id_pelanggan, id_status))
        t = cur.fetchone()

        if t:
            id_transaksi = t[0]
        else:
            cur.execute("""
                INSERT INTO transaksi (id_pelanggan, id_status_transaksi, tgl_transaksi)
                VALUES (%s, %s, CURRENT_DATE) RETURNING id_transaksi
            """, (id_pelanggan, id_status))
            id_transaksi = cur.fetchone()[0]

        while True:
            # Tampilkan daftar produk
            cur.execute("""
                SELECT p.id_produk, j.nama_jenis, p.stok, j.harga_produk, p.tgl_update_stok
                FROM produk p
                JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
                ORDER BY p.id_produk
            """)
            daftar_produk = cur.fetchall()

            if not daftar_produk:
                print(Fore.YELLOW + "Belum ada produk tersedia." + Style.RESET_ALL)
                break

            headers = ["ID Produk", "Jenis Produk", "Stok", "Harga (Rp)", "Update Stok"]
            print(tabulate(daftar_produk, headers=headers, tablefmt="fancy_grid"))

            id_produk_in = input("Masukkan ID Produk [Enter untuk batal]: ")
            if id_produk_in.strip() == "":
                print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                break
            qty_in = input("Masukkan jumlah [Enter untuk batal]: ")
            if qty_in.strip() == "":
                print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
                break

            try:
                id_produk = int(id_produk_in)
                quantity = int(qty_in)
            except ValueError:
                print(Fore.RED + "Input harus angka!" + Style.RESET_ALL)
                continue

            # Cek stok
            cur.execute("SELECT stok FROM produk WHERE id_produk = %s", (id_produk,))
            row = cur.fetchone()
            if not row:
                print(Fore.RED + "Produk tidak ditemukan." + Style.RESET_ALL)
                continue

            stok_tersedia = row[0]
            if quantity > stok_tersedia:
                print(Fore.RED + f"Stok tidak cukup. Stok tersedia: {stok_tersedia}" + Style.RESET_ALL)
                continue

            # Ambil harga produk
            cur.execute("""
                SELECT j.harga_produk
                FROM produk p
                JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
                WHERE p.id_produk = %s
            """, (id_produk,))
            row = cur.fetchone()
            if not row:
                print(Fore.RED + "Harga produk tidak ditemukan." + Style.RESET_ALL)
                continue
            harga_satuan = row[0]
            total_harga = harga_satuan * quantity

            # Konfirmasi sebelum insert
            print("\n--- Konfirmasi Produk ---")
            print(f"ID Produk   : {id_produk}")
            print(f"Jumlah      : {quantity}")
            print(f"Harga Satuan: {harga_satuan}")
            print(f"Total Harga : {total_harga}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Produk batal ditambahkan." + Style.RESET_ALL)
                continue

            # Insert detail transaksi
            cur.execute("""
                INSERT INTO detail_transaksi (id_transaksi, id_produk, quantity, harga)
                VALUES (%s, %s, %s, %s)
            """, (id_transaksi, id_produk, quantity, total_harga))

            # Update stok produk
            cur.execute("""
                UPDATE produk
                SET stok = stok - %s, tgl_update_stok = CURRENT_DATE
                WHERE id_produk = %s
            """, (quantity, id_produk))

            conn.commit()
            print(Fore.GREEN + f"Produk {id_produk} x{quantity} berhasil ditambahkan ke keranjang." + Style.RESET_ALL)

            lanjut = input("Tambah produk lain? (y/n): ").strip().lower()
            if lanjut != "y":
                break

        print(Fore.GREEN + "Selesai memilih produk. Semua pilihan sudah masuk ke keranjang." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal memilih produk:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def lihat_keranjang(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Lihat Keranjang ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Ambil status 'proses'
        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'proses' tidak ada di status_transaksi." + Style.RESET_ALL)
            return
        id_status = s[0]

        # Cari transaksi aktif
        cur.execute("""
            SELECT id_transaksi, id_metode_pembayaran
            FROM transaksi
            WHERE id_pelanggan = %s AND id_status_transaksi = %s
            ORDER BY id_transaksi DESC
            LIMIT 1
        """, (id_pelanggan, id_status))
        t = cur.fetchone()

        if not t:
            print(Fore.YELLOW + "Keranjang kosong. Belum ada transaksi aktif." + Style.RESET_ALL)
            return

        id_transaksi, id_metode = t

        # Ambil detail keranjang
        cur.execute("""
            SELECT j.nama_jenis, d.quantity, d.harga
            FROM detail_transaksi d
            JOIN produk p ON d.id_produk = p.id_produk
            JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
            WHERE d.id_transaksi = %s
        """, (id_transaksi,))
        items = cur.fetchall()

        if not items:
            print(Fore.YELLOW + "Keranjang masih kosong." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "\n=== Isi Keranjang ===" + Style.RESET_ALL)
            headers = ["Produk", "Jumlah", "Subtotal (Rp)"]
            print(tabulate(items, headers=headers, tablefmt="fancy_grid"))

            total = sum([row[2] for row in items])
            print(Fore.GREEN + f"\nTotal Keranjang: Rp {total}" + Style.RESET_ALL)

        # Tampilkan metode pembayaran
        if id_metode:
            cur.execute("""
                SELECT id_metode_pembayaran, nama_transaksi 
                FROM metode_pembayaran 
                WHERE id_metode_pembayaran = %s
            """, (id_metode,))
            metode = cur.fetchone()
            if metode:
                print(Fore.GREEN + f"\nMetode Pembayaran Aktif: {metode[1]} (ID: {metode[0]})" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "\nMetode pembayaran belum dipilih." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "\nMetode pembayaran belum dipilih." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal menampilkan keranjang:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def edit_keranjang(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Edit Keranjang ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Cari transaksi aktif dengan status 'proses'
        cur.execute("""
            SELECT t.id_transaksi
            FROM transaksi t
            JOIN status_transaksi s ON t.id_status_transaksi = s.id_status_transaksi
            WHERE t.id_pelanggan = %s AND s.nama_status = 'proses'
            ORDER BY t.id_transaksi DESC
            LIMIT 1
        """, (id_pelanggan,))
        t = cur.fetchone()

        if not t:
            print(Fore.YELLOW + "Keranjang kosong. Belum ada transaksi aktif." + Style.RESET_ALL)
            return

        id_transaksi = t[0]

        # Ambil isi keranjang
        cur.execute("""
            SELECT d.id_detail_transaksi, j.nama_jenis, d.quantity, d.harga
            FROM detail_transaksi d
            JOIN produk p ON d.id_produk = p.id_produk
            JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
            WHERE d.id_transaksi = %s
        """, (id_transaksi,))
        items = cur.fetchall()

        if not items:
            print(Fore.YELLOW + "Keranjang masih kosong." + Style.RESET_ALL)
            return

        headers = ["ID Detail", "Produk", "Jumlah", "Subtotal (Rp)"]
        print(tabulate(items, headers=headers, tablefmt="fancy_grid"))

        id_detail_in = input("Masukkan ID Detail yang ingin diubah/hapus [Enter untuk batal]: ")
        if id_detail_in.strip() == "":
            print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
            return
        try:
            id_detail = int(id_detail_in)
        except ValueError:
            print(Fore.RED + "ID Detail harus angka." + Style.RESET_ALL)
            return

        pilihan = input("Ketik 'ubah' untuk ubah jumlah, 'hapus' untuk hapus produk [Enter untuk batal]: ").lower()
        if pilihan.strip() == "":
            print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
            return

        if pilihan == "ubah":
            new_qty_in = input("Masukkan jumlah baru [Enter untuk batal]: ")
            if new_qty_in.strip() == "":
                print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
                return
            try:
                new_qty = int(new_qty_in)
            except ValueError:
                print(Fore.RED + "Jumlah harus angka." + Style.RESET_ALL)
                return

            cur.execute("""
                SELECT j.harga_produk
                FROM detail_transaksi d
                JOIN produk p ON d.id_produk = p.id_produk
                JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
                WHERE d.id_detail_transaksi = %s
            """, (id_detail,))
            row = cur.fetchone()
            if not row:
                print(Fore.RED + "Produk tidak ditemukan." + Style.RESET_ALL)
                return

            harga_satuan = row[0]
            total_harga = harga_satuan * new_qty

            # Konfirmasi sebelum update
            print("\n--- Konfirmasi Ubah ---")
            print(f"ID Detail : {id_detail}")
            print(f"Jumlah Baru: {new_qty}")
            print(f"Subtotal   : {total_harga}")
            konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Edit dibatalkan." + Style.RESET_ALL)
                return

            cur.execute("""
                UPDATE detail_transaksi
                SET quantity = %s, harga = %s
                WHERE id_detail_transaksi = %s
            """, (new_qty, total_harga, id_detail))
            conn.commit()
            print(Fore.GREEN + "Jumlah produk berhasil diubah." + Style.RESET_ALL)

        elif pilihan == "hapus":
            # Konfirmasi sebelum hapus
            print("\n--- Konfirmasi Hapus ---")
            print(f"ID Detail : {id_detail}")
            konfirmasi = input("Apakah yakin ingin menghapus produk ini? (y/n): ").strip().lower()
            if konfirmasi != "y":
                print(Fore.YELLOW + "Hapus dibatalkan." + Style.RESET_ALL)
                return

            cur.execute("DELETE FROM detail_transaksi WHERE id_detail_transaksi = %s", (id_detail,))
            conn.commit()
            print(Fore.GREEN + "Produk berhasil dihapus dari keranjang." + Style.RESET_ALL)

        else:
            print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal edit keranjang:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def pilih_metode_pembayaran(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Pilih Metode Pembayaran ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Ambil status 'proses'
        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'proses' tidak ditemukan." + Style.RESET_ALL)
            return
        id_status = s[0]

        # Cari transaksi aktif
        cur.execute("""
            SELECT id_transaksi
            FROM transaksi
            WHERE id_pelanggan = %s AND id_status_transaksi = %s
            ORDER BY id_transaksi DESC
            LIMIT 1
        """, (id_pelanggan, id_status))
        t = cur.fetchone()

        if not t:
            print(Fore.YELLOW + "Tidak ada transaksi aktif. Silakan pilih produk dulu." + Style.RESET_ALL)
            return

        id_transaksi = t[0]

        # Ambil daftar metode pembayaran
        cur.execute("SELECT id_metode_pembayaran, nama_metode_pembayaran FROM metode_pembayaran")
        metode = cur.fetchall()

        if not metode:
            print(Fore.YELLOW + "Belum ada metode pembayaran tersedia." + Style.RESET_ALL)
            return

        print(Fore.GREEN + "\n=== Daftar Metode Pembayaran ===" + Style.RESET_ALL)
        for m in metode:
            print(f"{m[0]}. {m[1]}")

        pilihan_in = input("Masukkan ID Metode Pembayaran [Enter untuk batal]: ")
        if pilihan_in.strip() == "":
            print(Fore.YELLOW + "Dibatalkan, kembali ke menu utama." + Style.RESET_ALL)
            return
        try:
            pilihan = int(pilihan_in)
        except ValueError:
            print(Fore.RED + "Input harus angka!" + Style.RESET_ALL)
            return

        cur.execute("SELECT id_metode_pembayaran, nama_metode_pembayaran FROM metode_pembayaran WHERE id_metode_pembayaran = %s", (pilihan,))
        cek = cur.fetchone()
        if not cek:
            print(Fore.RED + "Metode pembayaran tidak valid." + Style.RESET_ALL)
            return

        # Konfirmasi sebelum update
        print("\n--- Konfirmasi Metode Pembayaran ---")
        print(f"ID   : {cek[0]}")
        print(f"Nama : {cek[1]}")
        konfirmasi = input("Apakah data sudah benar? (y/n): ").strip().lower()
        if konfirmasi != "y":
            print(Fore.YELLOW + "Update dibatalkan." + Style.RESET_ALL)
            return

        cur.execute("""
            UPDATE transaksi
            SET id_metode_pembayaran = %s
            WHERE id_transaksi = %s
        """, (pilihan, id_transaksi))
        conn.commit()

        print(Fore.GREEN + "Metode pembayaran berhasil dipilih." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal memilih metode pembayaran:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def edit_metode_pembayaran(id_pelanggan):
    print(Fore.CYAN + "=== Edit Metode Pembayaran ===" + Style.RESET_ALL)
    conn, cur = connectDB()
    if not conn: return

    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
    s = cur.fetchone()
    if not s:
        print("Status 'proses' tidak ditemukan.")
        cur.close(); conn.close()
        return
    id_status = s[0]

    cur.execute("""
        SELECT id_transaksi, id_metode_pembayaran
        FROM transaksi
        WHERE id_pelanggan = %s AND id_status_transaksi = %s
        ORDER BY id_transaksi DESC
        LIMIT 1
    """, (id_pelanggan, id_status))
    t = cur.fetchone()
    if not t:
        print("Tidak ada transaksi aktif untuk pelanggan ini.")
        cur.close(); conn.close()
        return
    id_transaksi = t[0]

    cur.execute("SELECT id_metode_pembayaran, nama_metode_pembayaran FROM metode_pembayaran ORDER BY id_metode_pembayaran")
    metode = cur.fetchall()
    headers = ["ID Metode", "Nama Metode"]
    print(tabulate(metode, headers=headers, tablefmt="fancy_grid"))

    try:
        pilihan = int(input("Masukkan ID Metode Pembayaran baru: "))
    except ValueError:
        print("Input harus angka!")
        cur.close(); conn.close()
        return

    cur.execute("SELECT id_metode_pembayaran FROM metode_pembayaran WHERE id_metode_pembayaran = %s", (pilihan,))
    cek = cur.fetchone()
    if not cek:
        print("Metode pembayaran tidak valid.")
        cur.close(); conn.close()
        return

    cur.execute("""
        UPDATE transaksi
        SET id_metode_pembayaran = %s
        WHERE id_transaksi = %s
    """, (pilihan, id_transaksi))
    conn.commit()
    print("Metode pembayaran berhasil diganti untuk transaksi aktif.")

    cur.close(); conn.close()
    prompt_enter()

def checkout(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Checkout ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        # Ambil status transaksi
        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'proses' tidak ada di status_transaksi." + Style.RESET_ALL)
            return
        id_status_proses = s[0]

        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'selesai'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'selesai' tidak ada di status_transaksi." + Style.RESET_ALL)
            return
        id_status_selesai = s[0]

        cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'dibatalkan'")
        s = cur.fetchone()
        if not s:
            print(Fore.RED + "Status 'dibatalkan' tidak ada di status_transaksi." + Style.RESET_ALL)
            return
        id_status_batal = s[0]

        # Cari transaksi aktif
        cur.execute("""
            SELECT id_transaksi FROM transaksi
            WHERE id_pelanggan = %s AND id_status_transaksi = %s
            ORDER BY id_transaksi DESC LIMIT 1
        """, (id_pelanggan, id_status_proses))
        transaksi = cur.fetchone()
        if not transaksi:
            print(Fore.YELLOW + "Tidak ada transaksi aktif." + Style.RESET_ALL)
            return
        id_transaksi = transaksi[0]

        # Ambil detail transaksi
        cur.execute("""
            SELECT d.id_produk, d.quantity, jp.harga_produk
            FROM detail_transaksi d
            JOIN produk p ON d.id_produk = p.id_produk
            JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
            WHERE d.id_transaksi = %s
        """, (id_transaksi,))
        items = cur.fetchall()
        if not items:
            print(Fore.YELLOW + "Keranjang kosong." + Style.RESET_ALL)
            return

        total_belanja = sum(qty * harga for _, qty, harga in items)

        # Konfirmasi sebelum checkout/batal
        print("\n--- Ringkasan Transaksi ---")
        print(f"ID Transaksi : {id_transaksi}")
        print(f"Jumlah Item  : {len(items)}")
        print(f"Total Belanja: Rp {total_belanja}")
        aksi = input("Lanjut checkout atau dibatalkan? (checkout/dibatalkan) [Enter untuk batal]: ").strip().lower()
        if aksi == "":
            print(Fore.YELLOW + "Checkout dibatalkan." + Style.RESET_ALL)
            return

        if aksi == "checkout":
            cur.execute("""
                UPDATE transaksi
                SET id_status_transaksi = %s, tgl_transaksi = CURRENT_DATE
                WHERE id_transaksi = %s
            """, (id_status_selesai, id_transaksi))
            conn.commit()
            print(Fore.GREEN + "Checkout berhasil!" + Style.RESET_ALL)
            print(Fore.GREEN + f"Total belanja: Rp {total_belanja}" + Style.RESET_ALL)

        elif aksi == "dibatalkan":
            for id_produk, qty, _ in items:
                cur.execute("""
                    UPDATE produk
                    SET stok = stok + %s, tgl_update_stok = CURRENT_DATE
                    WHERE id_produk = %s
                """, (qty, id_produk))

            cur.execute("""
                UPDATE transaksi
                SET id_status_transaksi = %s
                WHERE id_transaksi = %s
            """, (id_status_batal, id_transaksi))
            conn.commit()
            print(Fore.GREEN + f"Transaksi {id_transaksi} dibatalkan, stok dikembalikan." + Style.RESET_ALL)

        else:
            print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + "Gagal checkout:", e, Style.RESET_ALL)
        conn.rollback()
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

def lihat_riwayat_transaksi_pembelian(id_pelanggan):
    clear_screen()
    print(Fore.CYAN + "=== Riwayat Transaksi Pembelian ===" + Style.RESET_ALL)

    conn, cur = connectDB()
    if not conn:
        prompt_enter()
        return

    try:
        query = """
            SELECT t.id_transaksi, t.tgl_transaksi, COALESCE(mp.nama_metode_pembayaran, '-') AS metode_bayar,
                   SUM(dt.quantity * jp.harga_produk) AS total_belanja
            FROM transaksi t
            LEFT JOIN metode_pembayaran mp ON t.id_metode_pembayaran = mp.id_metode_pembayaran
            JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
            JOIN produk p ON dt.id_produk = p.id_produk
            JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
            JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
            WHERE t.id_pelanggan = %s AND st.nama_status = 'selesai'
            GROUP BY t.id_transaksi, t.tgl_transaksi, mp.nama_metode_pembayaran
            ORDER BY t.tgl_transaksi DESC
        """
        cur.execute(query, (id_pelanggan,))
        riwayat = cur.fetchall()

        if not riwayat:
            print(Fore.YELLOW + "Belum ada transaksi selesai." + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "\n=== Daftar Riwayat Transaksi Pembelian ===" + Style.RESET_ALL)
            headers = ["ID Transaksi", "Tanggal", "Metode Bayar", "Total Belanja (Rp)"]
            print(tabulate(riwayat, headers=headers, tablefmt="fancy_grid"))

    except Exception as e:
        print(Fore.RED + "Gagal menampilkan riwayat transaksi:", e, Style.RESET_ALL)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

    prompt_enter()

main()