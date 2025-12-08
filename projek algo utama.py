import psycopg2
import pandas as pd 
from tabulate import tabulate
from datetime import datetime   
import logo
def connectDB():
    try:
        conn = psycopg2.connect(host="localhost", user ="postgres", password="rosa123", dbname="proyek akhir")
        cur = conn.cursor()
        print("Database connected successfully")
        return conn, cur
    except Exception as e:
        print("Failed to connect to database")
        print("Error detail:")
        return None, None
    
def main():
    while True:
        Menu = [
            ["No", "Opsi"], 
            [1., "Register"],
            [2., "Login"],
            [3., "Keluar"]
        ]
        print("\n=== Menu Utama ===")
        print(tabulate(Menu, headers="firstrow", tablefmt="fancy_grid"))
        pilihan = int(input("Pilih opsi (1/2/3): "))
        if pilihan == 1:
            registerasi()
        elif pilihan == 2:
            login()
        elif pilihan == 3:
            print("Program selesai. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")
    
def registerasi():
    print("==== Registrasi Pelanggan ====")
    nama_pelanggan= input("Masukkan nama pelanggan: ")
    username_pelanggan = input("Masukkan username: ")
    kata_sandi_pelanggan = input("Masukkan kata_sandi: ")
    no_telp_pelanggan = input("Masukkan nomor telepon: ")

    conn, cur = connectDB()
    query = """
        INSERT INTO pelanggan (nama_pelanggan, username_pelanggan, kata_sandi_pelanggan, no_telp_pelanggan)
        VALUES (%s, %s, %s, %s)
    """
    cur.execute(query, (nama_pelanggan, username_pelanggan, kata_sandi_pelanggan, no_telp_pelanggan))
    conn.commit()
    print("Registrasi berhasil!")
    main()
    
    cur.close()
    conn.close()


def login():
    while True:
        Login = [
            ["No.", "Opsi"],
            [1., "Karyawan"],
            [2., "Pelanggan"]
        ]
        print("\n==== Login ====")
        print(tabulate(Login, headers="firstrow", tablefmt="fancy_grid" ))
        pilihan = int(input("Pilih opsi (1/2): "))
        if pilihan == 1:
            login_karyawan()
        elif pilihan == 2:
            login_pelanggan()
            break
        else:
            print("Pilihan tidak valid, coba lagi.")

def login_karyawan():
    print("==== Login Karyawan ====")
    username = input("Username: ")
    password = input("Password: ")

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
    print(f"\nSelamat datang {nama_lengkap}! Anda login sebagai {role}.\n")

    if karyawan:
        role = karyawan['role']
        if role == 'Manajer Produksi':
            halaman_menu_manajer_produksi()
        elif role == 'Admin Produksi':
            halaman_menu_admin_produksi()
        elif role == 'Admin Gudang':
            halaman_menu_admin_gudang()
        else:
            print("Role tidak dikenali.")
    else:
        print("Login gagal. Username atau password salah.")

def cari_karyawan_di_database(username, password):
    conn, cur = connectDB()
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
        cur.close()
        conn.close()
        return karyawan
    cur.close()
    conn.close()
    return None

def login_pelanggan():
    print("==== Login Pelanggan ====")
    username_pelanggan = input("Masukkan username: ")
    kata_sandi_pelanggan = input("Masukkan kata_sandi: ")

    conn, cur = connectDB()
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
        print(f"\nSelamat datang {nama_pelanggan}! Anda berhasil login sebagai Pelanggan.\n")
        halaman_menu_pelanggan(id_pelanggan = result[0])

    else:
        print("Login gagal! Username atau kata sandi salah.")
    cur.close()
    conn.close()
def halaman_menu_admin_produksi():
    while True:
        menu = [
            [1, "Lihat Biodata"],
            [2, "Edit Biodata"],
            [3, "Input Hasil Panen"],
            [4, "Hapus Hasil Panen"],
            [5, "Lihat Laporan Hasil Panen"],
            [6, "Edit Hasil Panen"],
            [7, "Input Produksi"],
            [8, "Edit Produksi"],
            [9, "Hapus Produksi"],
            [10, "Perbarui Status Produksi"],
            [11, "Lihat Laporan Produksi"],
            [12, "Logout"]
        ]
        print("\n=== Halaman Menu Admin Produksi ===")
        print(tabulate(menu, headers=["No", "Menu"], tablefmt="fancy_grid"))
        pilihan_adp = int(input("Pilih menu: "))

        if pilihan_adp == 1:
             lihat_biodata_karyawan()
        elif pilihan_adp == 2:
            edit_bio_karyawan()
        elif pilihan_adp == 3:
            input_hp()
        elif pilihan_adp == 4:
            hapus_hp()
        elif pilihan_adp == 5:
           lihat_laporan_hp()
        elif pilihan_adp == 6:
            edit_hp()
        elif pilihan_adp == 7:
            input_produksi()
        elif pilihan_adp == 8:
            edit_produksi()
        elif pilihan_adp == 9:  
            hapus_produksi()
        elif pilihan_adp == 10:
            perbarui_status_produksi()
        elif pilihan_adp == 11:
            lihat_laporan_produksi()
        elif pilihan_adp == 12:
            logout()
            exit()
        else:
            print("Pilihan tidak valid, coba lagi.")

def edit_bio_karyawan():
    print("=== Edit Biodata ===")
    conn, cur = connectDB()
    username_karyawan = input("Masukkan username: ")
    query = "SELECT * FROM karyawan WHERE username_karyawan = %s"
    cur.execute(query, (username_karyawan,))
    result = cur.fetchone()

    if result:
        print("Masukkan data baru (isi kembali data untuk tidak mengubah):")
        nama_baru = input(f"Nama ({result[1]}): ") or result[1]
        username_baru = input(f"Username ({result[2]}): ") or result[2] 
        kata_sandi_baru = input(f"Kata Sandi ({result[3]}): ") or result[3]
        no_telp_baru = input(f"No Telepon ({result[6]}): ") or result[6]
    else:
        print("Data biodata tidak ditemukan.")
    cur.close()
    conn.close()

def lihat_biodata_karyawan():
    print("=== Lihat Biodata ===")
    conn, cur = connectDB()
    username_karyawan = input("Masukkan username: ")
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
        print("\n=== Biodata Admin Produksi ===")
        print(tabulate(biodata, headers=["Data", "Keterangan"], tablefmt="fancy_grid"))
    else:
        print("Data biodata tidak ditemukan.")
    cur.close()
    conn.close()

def input_hp():
    print("=== Input Hasil Panen ===")
    conn, cur = connectDB()
    hasil_panen = float(input("Masukkan jumlah hasil panen (kg): "))
    tanggal_panen = input("Masukkan tanggal panen (YYYY-MM-DD): ")
    id_karyawan = int(input("Masukkan ID karyawan: "))
    query = """
        INSERT INTO hasil_panen (jmlh_panen, tgl_panen,id_karyawan)
        VALUES (%s, %s, %s)
        
    """ 
    cur.execute(query, (hasil_panen, tanggal_panen, id_karyawan))
    conn.commit()
    print("Input hasil panen berhasil!")
    cur.close()
    conn.close()

def hapus_hp():
    print("=== Hapus Hasil Panen ===")
    conn, cur = connectDB()
    id_hp = int(input("Masukkan ID hasil panen yang akan dihapus: "))
    query = "DELETE FROM hasil_panen WHERE id_hp = %s"
    cur.execute(query, (id_hp,))
    conn.commit()
    print("Hasil Panen berhasil dihapus.")
    cur.close()
    conn.close()

def edit_hp():
    print("=== Edit Hasil Panen ===")
    conn, cur = connectDB()
    id_hp = int(input("Masukkan ID hasil panen yang akan diedit: "))
    query = "SELECT * FROM hasil_panen WHERE id_hp = %s"
    cur.execute(query, (id_hp,))
    result = cur.fetchone()

    if result:
        print("Masukkan data baru (isi ulang untuk data yang tidak diubah):")
        tgl_panen_baru = input(f"Tanggal Panen ({result[1]}): ") or result[1]
        jmlh_panen_baru = input(f"Jumlah Panen ({result[2]}): ") or result[2] 
        id_karyawan_baru = input(f"ID Karyawan ({result[3]}): ") or result[3]

        update_query = """
            UPDATE hasil_panen
            SET tgl_panen = %s, jmlh_panen = %s, id_karyawan = %s
            WHERE id_hp = %s
        """
        cur.execute(update_query, (tgl_panen_baru, jmlh_panen_baru, id_karyawan_baru, id_hp))
        conn.commit()
        print("Hasil Panen berhasil diperbarui.")
    else:
        print("Data hasil panen tidak ditemukan.")

    cur.close()
    conn.close() 

def lihat_laporan_hp():    
    print("=== Lihat Laporan Hasil Panen ===")
    conn, cur = connectDB()
    query =  """
        SELECT hp.id_hp, hp.jmlh_panen, hp.tgl_panen, k.nama_karyawan
        FROM hasil_panen hp
        JOIN karyawan k ON hp.id_karyawan = k.id_karyawan
    """
    cur.execute(query)
    results = cur.fetchall()    
    df = pd.DataFrame(results, columns=['ID Hasil Panen', 'Hasil Panen (kg)', 'Tanggal Panen', 'Nama Karyawan'])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    cur.close()
    conn.close()

def input_produksi():
    print("=== Input Produksi ===")
    conn, cur = connectDB()
    tanggal_produksi = input("Masukkan tanggal produksi (YYYY-MM-DD): ")
    jumlah_produksi = float(input("Masukkan jumlah produksi (kg): "))
    id_karyawan = int(input("Masukkan ID karyawan: "))
    id_hp = int(input("Masukkan ID hasil panen: "))
    id_status_produksi = int(input("Masukkan ID status panen (1. selesai/2. ditunda/3. proses): "))
    query = """
        INSERT INTO produksi (tgl_produksi, jmlh_produksi, id_karyawan, id_hp, id_status_produksi)
        VALUES (%s, %s, %s, %s, %s)
    """     
    cur.execute(query, (tanggal_produksi, jumlah_produksi, id_karyawan, id_hp, id_status_produksi))
    conn.commit()
    print("Input produksi berhasil!")
    cur.close()
    conn.close()

def perbarui_status_produksi():
    print("=== Perbarui Status Produksi ===")
    conn, cur = connectDB()
    id_produksi = int(input("Masukkan ID produksi yang akan diperbarui: "))
    status_baru = int(input("Masukkan status produksi baru (1. selesai/2. ditunda/3. proses): "))

    if status_baru == 1:  
        query = """
            UPDATE produksi
            SET id_status_produksi = %s, tgl_selesai = %s
            WHERE id_produksi = %s"""
        cur.execute(query, (status_baru, datetime.now(), id_produksi))
    else: 
        query = """
            UPDATE produksi
            SET id_status_produksi = %s, tgl_selesai = NULL
            WHERE id_produksi = %s"""
        cur.execute(query, (status_baru, id_produksi))
    conn.commit()
    print("Status produksi berhasil diperbarui!")
    cur.close()
    conn.close()

def lihat_laporan_produksi():
    print("=== Lihat Laporan Produksi ===")
    conn, cur = connectDB()
    query =  """
        SELECT p.id_produksi, p.tgl_produksi, p.tgl_selesai, p.jmlh_produksi,
               k.nama_karyawan, hp.jmlh_panen, sp.nama_status
        FROM produksi p
        JOIN karyawan k ON p.id_karyawan = k.id_karyawan
        JOIN hasil_panen hp ON p.id_hp = hp.id_hp
        JOIN status_produksi sp ON p.id_status_produksi = sp.id_status_produksi"""
    cur.execute(query)
    results = cur.fetchall()        
    df = pd.DataFrame(results, columns=['ID Produksi', 'Tanggal Produksi','Tanggal Selesai', 'Jumlah Produksi', 'Nama Karyawan', 'Jumlah Hasil Panen (kg)', 'Status Produksi' ])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    cur.close()
    conn.close()

def edit_produksi():
    print("=== Edit Produksi ===")
    conn, cur = connectDB()
    id_produksi = int(input("Masukkan ID produksi yang akan diedit: "))
    query = "SELECT * FROM produksi WHERE id_produksi = %s"
    cur.execute(query, (id_produksi,))
    result = cur.fetchone()

    if result:
        print("Masukkan data baru (isi kembali untuk tidak mengubah):")
        tgl_produksi_baru = input(f"Tanggal Produksi ({result[1]}): ") or result[1]
        jmlh_produksi_baru = input(f"Jumlah Produksi ({result[3]}): ") or result[3]
        id_karyawan_baru = input(f"ID Karyawan ({result[4]}): ") or result[4]
        id_hp_baru = input(f"ID Hasil Panen ({result[5]}): ") or result[5]
        id_status_produksi_baru = input(f"ID Status Produksi ({result[6]}): ") or result[6]

        if id_status_produksi_baru == 1:  
            query = """
                UPDATE produksi
                SET id_status_produksi = %s, tgl_selesai = %s
                WHERE id_produksi = %s"""
            cur.execute(query, (id_status_produksi_baru, datetime.now(), id_produksi))
        else: 
            query = """
                UPDATE produksi
                SET id_status_produksi = %s, tgl_selesai = NULL
                WHERE id_produksi = %s"""
            cur.execute(query, (id_status_produksi_baru, id_produksi))

            update_query = """
                UPDATE produksi
                SET tgl_produksi = %s, tgl_selesai = %s, jmlh_produksi = %s, id_karyawan = %s, id_hp = %s, id_status_produksi = %s
                WHERE id_produksi = %s
            """
            cur.execute(update_query, (tgl_produksi_baru, datetime.now(), jmlh_produksi_baru, id_karyawan_baru, id_hp_baru, id_status_produksi_baru, id_produksi))
            conn.commit()
            print("Produksi berhasil diperbarui.")
    else:
        print("Data produksi tidak ditemukan.")

    cur.close()
    conn.close()

def hapus_produksi():
    print("=== Hapus Produksi ===")
    conn, cur = connectDB()
    id_produksi = int(input("Masukkan ID produksi yang akan dihapus: "))
    query = "DELETE FROM produksi WHERE id_produksi = %s"
    cur.execute(query, (id_produksi,))
    conn.commit()
    print("Produksi berhasil dihapus.")
    cur.close()
    conn.close()

def logout():
    print("Anda telah keluar dari sistem.")
    print("=== Logout ===")

def halaman_menu_admin_gudang():
    while True:
        menu = [
            [1, "Lihat Biodata"],
            [2, "Edit Biodata"],
            [3, "Lihat Laporan Produksi"],
            [4, "Input Produk"],
            [5, "Hapus Produk"],
            [6, "Lihat Laporan Produk"],
            [7, "Edit Data Produk"],
            [8, "Update Status Transaksi"],
            [9, "Lihat Laporan Transaksi"],
            [10, "Logout"]
        ]
        print("\n=== Halaman Menu Admin Gudang ===")
        print(tabulate(menu, headers=["No", "Menu"], tablefmt="fancy_grid"))
        pilihan_adg = int(input("Pilih menu: "))

        if pilihan_adg == 1:
            lihat_biodata_karyawan()
        elif pilihan_adg == 2:
            edit_bio_karyawan()
        elif pilihan_adg == 3:
            lihat_laporan_produksi()
        elif pilihan_adg == 4:
            input_produk()
        elif pilihan_adg == 5:
            hapus_produk()
        elif pilihan_adg == 6:
            lihat_laporan_produk()
        elif pilihan_adg == 7:
            edit_produk()
        elif pilihan_adg == 8:
            update_status_transaksi()
        elif pilihan_adg == 9:
            lihat_laporan_transaksi()
        elif pilihan_adg == 10:
            logout()
            exit()
        else:
            print("Pilihan tidak valid, coba lagi.")

def input_produk():
    print("=== Input Produk ===")
    conn, cur = connectDB()
    jumlah_dibutuhkan = int(input("Masukkan jumlah stok: "))
    id_jenis_produk = int(input("Masukkan id jenis (1.Fresh, 2.Frozen, 3.Jus): "))

    query = """
        SELECT id_produksi, jmlh_produksi
        FROM produksi
        WHERE jmlh_produksi > 0
        ORDER BY tgl_produksi ASC
    """
    cur.execute(query)
    produksis = cur.fetchall()

    sisa = jumlah_dibutuhkan
    for id_produksi, jmlh_produksi in produksis:
        if sisa <= 0:
            break
        if jmlh_produksi >= sisa:
            cur.execute("""
                UPDATE produksi
                SET jmlh_produksi = jmlh_produksi - %s
                WHERE id_produksi = %s
            """, (sisa, id_produksi))
            sisa = 0
        else:
            cur.execute("""
                UPDATE produksi
                SET jmlh_produksi = 0
                WHERE id_produksi = %s
            """, (id_produksi,))
            sisa -= jmlh_produksi

    if sisa > 0:
        print("Stok habis! Tidak bisa memenuhi semua permintaan.")
    else:
        print("Input produk berhasil! Jumlah produksi berkurang.")
    conn.commit()
    cur.close()
    conn.close()

def lihat_laporan_produk():
    print("=== Lihat Laporan Produk ===")
    conn, cur = connectDB()
    query = """
        SELECT p.id_produk, j.nama_jenis, p.stok, p.tgl_update_stok, ps.jmlh_produksi
        FROM produk p
        JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
        JOIN produksi ps ON p.id_produksi = ps.id_produksi
    """
    cur.execute(query)
    results = cur.fetchall()
    df = pd.DataFrame(results, columns=['ID Produk', 'Jenis Produk', 'Jumlah Produk', 'Tanggal Update Stok', 'Jumlah Produksi'])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    cur.close()
    conn.close()

def edit_produk():
    print("=== Edit Produk ===")
    conn, cur = connectDB()
    id_produk = int(input("Masukkan ID produk yang akan diedit: "))
    query = "SELECT * FROM produk WHERE id_produk = %s"
    cur.execute(query, (id_produk,))
    result = cur.fetchone()

    if result:
        print("Masukkan data baru (isi kembali jika tidak mengubah data):")
        stok_baru = int(input(f"Stok baru ({result[1]}): ") or result[1])

        update_query = """
            UPDATE produk
            SET stok = %s, tgl_update_stok = %s
            WHERE id_produk = %s
        """
        cur.execute(update_query, (stok_baru, datetime.now(), id_produk))
        conn.commit()
        print("Produk berhasil diperbarui.")
    else:
        print("Data produk tidak ditemukan.")

    cur.close()
    conn.close()

def hapus_produk():
    print("=== Hapus Produk ===")
    conn, cur = connectDB()
    id_produk = int(input("Masukkan ID produk yang akan dihapus: "))
    query = "DELETE FROM produk WHERE id_produk = %s"
    cur.execute(query, (id_produk,))
    conn.commit()
    print("Produk berhasil dihapus.")
    cur.close()
    conn.close()

def update_status_transaksi():
    print("=== Input Status Transaksi ===")
    conn, cur = connectDB()
    id_transaksi = int(input("Masukkan ID transaksi yang akan diperbarui: "))
    status_baru = int(input("Masukkan status produksi baru (1. selesai/ 2. proses /3. dibatalkan): ")) 
    
    query = """
        UPDATE transaksi
        SET id_status_transaksi = %s
        WHERE id_transaksi = %s
    """
    cur.execute(query, (status_baru, id_transaksi))
    conn.commit()
    print("Status transaksi berhasil diperbarui!")
    cur.close()
    conn.close()

def lihat_laporan_transaksi():
    print("=== Lihat Laporan Transaksi ===")
    conn, cur = connectDB()
    query = """
        SELECT dt.id_detail_transaksi, t.id_transaksi, t.tgl_transaksi, jp.nama_jenis, dt.quantity, st.nama_status
        FROM transaksi t
        JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
        JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
        JOIN produk p ON dt.id_produk = p.id_produk
        JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
    """
    cur.execute(query)
    results = cur.fetchall()
    df = pd.DataFrame(results, columns=['ID Detail', 'ID Transaksi', 'Tanggal', 'Produk', 'Jumlah Produk', 'Status Transaksi'])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    cur.close()
    conn.close()

def halaman_menu_pelanggan(id_pelanggan):
    while True:
        print("=== AGROMAME: Menu Utama Pembelian ===")
        print("1. Lihat Biodata")
        print("2. Edit Biodata")
        print("3. Lihat Daftar Produk")
        print("4. Pilih Produk")
        print("5. Lihat Keranjang")
        print("6. Edit Keranjang")
        print("7. Pilih Metode Pembayaran")
        print("8. Edit Metode Pembayaran")
        print("9. Checkout")
        print("10. Lihat Riwayat Transaksi Pembelian")
        print("11. Logout")

        try:
            pilihan = int(input("Pilih menu: "))
        except ValueError:
            print("Input harus angka!")
            continue

        if pilihan == 1:
            lihat_biodata(id_pelanggan)
        elif pilihan == 2:
            edit_biodata(id_pelanggan)
        elif pilihan == 3:
            lihat_daftar_produk()
        elif pilihan == 4:
            pilih_produk(id_pelanggan)  
        elif pilihan == 5:
            lihat_keranjang(id_pelanggan)
        elif pilihan == 6:
            edit_keranjang(id_pelanggan)
        elif pilihan == 7:
            pilih_metode_pembayaran(id_pelanggan)
        elif pilihan == 8:
            edit_metode_pembayaran(id_pelanggan)
        elif pilihan == 9:
            checkout(id_pelanggan)
        elif pilihan == 10:
            lihat_riwayat_transaksi_pembelian(id_pelanggan)
        elif pilihan == 11:
            print("Logout berhasil.")
            exit()
        else:
            print("Pilihan tidak valid!")

def lihat_biodata(id_pelanggan):
    conn, cur = connectDB()

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
        print("=== BIODATA ===")
        if data[4]:  
            headers = ["Nama", "Username", "Kata Sandi", "No Telp", "Jalan", "Desa", "Kecamatan", "Kabupaten"]
            print(tabulate([data], headers=headers, tablefmt="fancy_grid"))
        else:  
            headers= ["Nama", "Username", "Kata Sandi", "No Telp", "Alamat"]
            row = [data[0], data[1], data[2], data[3], "Belum diisi"]
            print(tabulate([row], headers=headers, tablefmt="fancy_grid"))
    else:
        print("Data tidak ditemukan.")

    cur.close(); conn.close()

def edit_biodata(id_pelanggan):
    print("=== Edit Biodata ===")
    conn, cur = connectDB()

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
        print("Isi data baru (tekan Enter jika tidak ingin mengubah):")
        nama = input(f"Nama ({data[0]}): ") or data[0]
        user = input(f"Username ({data[1]}): ") or data[1]
        sandi = input(f"Kata Sandi ({data[2]}): ") or data[2]
        telp = input(f"No Telp ({data[3]}): ") or data[3]

        if data[4]: 
            jalan = input(f"Nama Jalan ({data[5]}): ") or data[5]
            desa = input(f"ID Desa ({data[6]} - {data[7]}): ") or data[6]

            cur.execute("""
                UPDATE alamat SET nama_jalan = %s, id_desa = %s
                WHERE id_alamat = %s
            """, (jalan, desa, data[4]))
        else:
            print("Alamat belum ada, silakan isi:")
            jalan = input("Nama Jalan: ")
            desa = input("ID Desa: ")

            cur.execute("""
                INSERT INTO alamat (nama_jalan, id_desa)
                VALUES (%s, %s) RETURNING id_alamat
            """, (jalan, desa))
            id_alamat_baru = cur.fetchone()[0]

            cur.execute("""
                UPDATE pelanggan SET id_alamat = %s
                WHERE id_pelanggan = %s
            """, (id_alamat_baru, id_pelanggan))

        cur.execute("""
            UPDATE pelanggan
            SET nama_pelanggan = %s,
                username_pelanggan = %s,
                kata_sandi_pelanggan = %s,
                no_telp_pelanggan = %s
            WHERE id_pelanggan = %s
        """, (nama, user, sandi, telp, id_pelanggan))

        conn.commit()
        print("Biodata berhasil diperbarui.")
    else:
        print("Data tidak ditemukan.")

    cur.close(); conn.close()

def lihat_daftar_produk():
    print("=== Lihat Daftar Produk ===")
    conn, cur = connectDB()

    query = """
    SELECT j.nama_jenis, p.stok, j.harga_produk, p.tgl_update_stok
    FROM produk p
    JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
    ORDER BY j.nama_jenis
    """
    cur.execute(query)
    data = cur.fetchall()

    if data:
        headers = ["Nama Jenis", "Stok", "Harga Produk (Rp)", "Update Stok"]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("Belum ada produk tersedia.")

    cur.close(); conn.close()

def pilih_produk(id_pelanggan):
    print("=== Pilih Produk ===")
    conn, cur = connectDB()

    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
    s = cur.fetchone()
    if not s:
        print("Status 'proses' tidak ada di status_transaksi.")
        cur.close(); conn.close()
        return
    id_status = s[0]

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
        cur.execute("""
            SELECT p.id_produk, j.nama_jenis, p.stok, j.harga_produk, p.tgl_update_stok
            FROM produk p
            JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
            ORDER BY p.id_produk
        """)
        daftar_produk = cur.fetchall()

        if not daftar_produk:
            print("Belum ada produk tersedia.")
            break

        headers = ["ID Produk", "Jenis Produk", "Stok", "Harga (Rp)", "Update Stok"]
        print(tabulate(daftar_produk, headers=headers, tablefmt="fancy_grid"))

        try:
            id_produk = int(input("Masukkan ID Produk: "))
            quantity = int(input("Masukkan jumlah: "))
        except ValueError:
            print("Input harus angka!")
            continue

        cur.execute("SELECT stok FROM produk WHERE id_produk = %s", (id_produk,))
        row = cur.fetchone()
        if not row:
            print("Produk tidak ditemukan.")
            continue

        stok_tersedia = row[0]
        if quantity > stok_tersedia:
            print("Stok tidak cukup. Stok tersedia:", stok_tersedia)
            continue

        cur.execute("""
            SELECT j.harga_produk
            FROM produk p
            JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
            WHERE p.id_produk = %s
        """, (id_produk,))
        row = cur.fetchone()
        if not row:
            print("Harga produk tidak ditemukan.")
            continue
        harga_satuan = row[0]
        total_harga = harga_satuan * quantity

        cur.execute("""
            INSERT INTO detail_transaksi (id_transaksi, id_produk, quantity, harga)
            VALUES (%s, %s, %s, %s)
        """, (id_transaksi, id_produk, quantity, total_harga))
        conn.commit()
        print(f"Produk {id_produk} x{quantity} berhasil ditambahkan ke keranjang.")

        lanjut = input("Tambah produk lain? (y/n): ").strip().lower()
        if lanjut != "y":
            break

    cur.close(); conn.close()
    print("Selesai memilih produk. Semua pilihan sudah masuk ke keranjang.")

def lihat_keranjang(id_pelanggan):
    print("=== Lihat Keranjang ===")
    conn, cur = connectDB()

    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
    s = cur.fetchone()
    if not s:
        print("Status 'proses' tidak ada di status_transaksi.")
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
        print("Keranjang kosong. Belum ada transaksi aktif.")
        cur.close(); conn.close()
        return

    id_transaksi, id_metode = t

    cur.execute("""
        SELECT j.nama_jenis, d.quantity, d.harga
        FROM detail_transaksi d
        JOIN produk p ON d.id_produk = p.id_produk
        JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
        WHERE d.id_transaksi = %s
    """, (id_transaksi,))
    items = cur.fetchall()

    if not items:
        print("Keranjang masih kosong.")
    else:
        headers = ["Produk", "Jumlah", "Subtotal (Rp)"]
        print(tabulate(items, headers=headers, tablefmt="fancy_grid"))

        total = sum([row[2] for row in items])
        print("\nTotal Keranjang: Rp", total)

    if id_metode:
        cur.execute("SELECT id_metode_pembayaran, nama_transaksi FROM metode_pembayaran WHERE id_metode_pembayaran = %s", (id_metode,))
        metode = cur.fetchone()
        if metode:
            print(f"\nMetode Pembayaran Aktif: {metode[1]} (ID: {metode[0]})")
        else:
            print("\nMetode pembayaran belum dipilih.")
    else:
        print("\nMetode pembayaran belum dipilih.")

    cur.close(); conn.close()

def edit_keranjang(id_pelanggan):
    print("=== Edit Keranjang ===")
    conn, cur = connectDB()

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
        print("Keranjang kosong. Belum ada transaksi aktif.")
        cur.close(); conn.close()
        return

    id_transaksi = t[0]

    cur.execute("""
        SELECT d.id_detail_transaksi, j.nama_jenis, d.quantity, d.harga
        FROM detail_transaksi d
        JOIN produk p ON d.id_produk = p.id_produk
        JOIN jenis_produk j ON p.id_jenis_produk = j.id_jenis_produk
        WHERE d.id_transaksi = %s
    """, (id_transaksi,))
    items = cur.fetchall()

    if not items:
        print("Keranjang masih kosong.")
        cur.close(); conn.close()
        return

    headers = ["ID Detail", "Produk", "Jumlah", "Subtotal (Rp)"]
    print(tabulate(items, headers=headers, tablefmt="fancy_grid"))

    try:
        id_detail = int(input("Masukkan ID Detail yang ingin diubah/hapus: "))
        pilihan = input("Ketik 'ubah' untuk ubah jumlah, 'hapus' untuk hapus produk: ").lower()
    except ValueError:
        print("Input harus angka!")
        cur.close(); conn.close()
        return

    if pilihan == "ubah":
        try:
            new_qty = int(input("Masukkan jumlah baru: "))
        except ValueError:
            print("Input harus angka!")
            cur.close(); conn.close()
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
            print("Produk tidak ditemukan.")
            cur.close(); conn.close()
            return

        harga_satuan = row[0]
        total_harga = harga_satuan * new_qty

        cur.execute("""
            UPDATE detail_transaksi
            SET quantity = %s, harga = %s
            WHERE id_detail_transaksi = %s
        """, (new_qty, total_harga, id_detail))
        conn.commit()
        print("Jumlah produk berhasil diubah.")

    elif pilihan == "hapus":
        cur.execute("DELETE FROM detail_transaksi WHERE id_detail_transaksi = %s", (id_detail,))
        conn.commit()
        print("Produk berhasil dihapus dari keranjang.")

    else:
        print("Pilihan tidak valid.")

    cur.close(); conn.close()

def pilih_metode_pembayaran(id_pelanggan):
    print("=== Pilih Metode Pembayaran ===")
    conn, cur = connectDB()

    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
    s = cur.fetchone()
    if not s:
        print("Status 'proses' tidak ditemukan.")
        cur.close(); conn.close()
        return
    id_status = s[0]

    cur.execute("""
        SELECT id_transaksi
        FROM transaksi
        WHERE id_pelanggan = %s AND id_status_transaksi = %s
        ORDER BY id_transaksi DESC
        LIMIT 1
    """, (id_pelanggan, id_status))
    t = cur.fetchone()

    if not t:
        print("Tidak ada transaksi aktif. Silakan pilih produk dulu.")
        cur.close(); conn.close()
        return

    id_transaksi = t[0]

    cur.execute("SELECT id_metode_pembayaran, nama_transaksi FROM metode_pembayaran")
    metode = cur.fetchall()

    if not metode:
        print("Belum ada metode pembayaran tersedia.")
        cur.close(); conn.close()
        return

    for m in metode:
        print(f"{m[0]}. {m[1]}")

    try:
        pilihan = int(input("Masukkan ID Metode Pembayaran: "))
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

    print("Metode pembayaran berhasil dipilih.")

    cur.close(); conn.close()

def edit_metode_pembayaran(id_pelanggan):
    print("=== Edit Metode Pembayaran ===")
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

    cur.execute("SELECT id_metode_pembayaran, nama_transaksi FROM metode_pembayaran ORDER BY id_metode_pembayaran")
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

def checkout(id_pelanggan):
    print("=== Checkout ===")
    conn, cur = connectDB()

    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'proses'")
    id_status_proses = cur.fetchone()[0]
    cur.execute("SELECT id_status_transaksi FROM status_transaksi WHERE nama_status = 'selesai'")
    id_status_selesai = cur.fetchone()[0]

    cur.execute("""
        SELECT id_transaksi FROM transaksi
        WHERE id_pelanggan = %s AND id_status_transaksi = %s
        ORDER BY id_transaksi DESC LIMIT 1
    """, (id_pelanggan, id_status_proses))
    transaksi = cur.fetchone()
    if not transaksi:
        print("Tidak ada transaksi aktif untuk checkout.")
        cur.close(); conn.close(); return
    id_transaksi = transaksi[0]

    cur.execute("""
        SELECT d.id_produk, d.quantity, jp.harga_produk, jp.id_jenis_produk
        FROM detail_transaksi d
        JOIN produk p ON d.id_produk = p.id_produk
        JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
        WHERE d.id_transaksi = %s
    """, (id_transaksi,))
    items = cur.fetchall()
    if not items:
        print("Keranjang kosong, tidak bisa checkout.")
        cur.close(); conn.close(); return

    total_belanja = 0
    for id_produk, qty, harga, id_jenis_produk in items:
        total_belanja += qty * harga

        cur.execute("SELECT stok FROM produk WHERE id_produk = %s", (id_produk,))
        if cur.fetchone()[0] < qty:
            print(f"Stok produk {id_produk} tidak cukup! Checkout dibatalkan.")
            conn.rollback(); cur.close(); conn.close(); return

        cur.execute("SELECT stok_total FROM jenis_produk WHERE id_jenis_produk = %s", (id_jenis_produk,))
        if cur.fetchone()[0] < qty:
            print(f"Stok jenis produk {id_jenis_produk} tidak cukup! Checkout dibatalkan.")
            conn.rollback(); cur.close(); conn.close(); return

        cur.execute("UPDATE produk SET stok = stok - %s WHERE id_produk = %s", (qty, id_produk))
        cur.execute("UPDATE jenis_produk SET stok_total = stok_total - %s WHERE id_jenis_produk = %s", (qty, id_jenis_produk))

    cur.execute("""
        UPDATE transaksi
        SET id_status_transaksi = %s, tgl_transaksi = CURRENT_DATE
        WHERE id_transaksi = %s
    """, (id_status_selesai, id_transaksi))

    conn.commit()
    print("Checkout berhasil!")
    print("Total belanja: Rp", total_belanja)
    cur.close(); conn.close()

def lihat_riwayat_transaksi_pembelian(id_pelanggan):
    print("=== Riwayat Transaksi Pembelian ===")
    conn, cur = connectDB()

    query = """
        SELECT t.id_transaksi, t.tgl_transaksi, COALESCE(mp.nama_transaksi, '-') AS metode_bayar,
               SUM(dt.quantity * jp.harga_produk) AS total_belanja
        FROM transaksi t
        LEFT JOIN metode_pembayaran mp ON t.id_metode_pembayaran = mp.id_metode_pembayaran
        JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
        JOIN produk p ON dt.id_produk = p.id_produk
        JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
        JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
        WHERE t.id_pelanggan = %s AND st.nama_status = 'selesai'
        GROUP BY t.id_transaksi, t.tgl_transaksi, mp.nama_transaksi
        ORDER BY t.tgl_transaksi DESC
    """
    cur.execute(query, (id_pelanggan,))
    riwayat = cur.fetchall()

    if not riwayat:
        print("Belum ada transaksi selesai.")
    else:
        headers = ["ID Transaksi", "Tanggal", "Metode Bayar", "Total Belanja (Rp)"]
        print(tabulate(riwayat, headers=headers, tablefmt="fancy_grid"))

    cur.close(); conn.close()
    
def halaman_menu_manajer_produksi():
    while True:
        menu = [
            ["1", "Lihat Biodata"],
            ["2", "Edit Biodata"],
            ["3", "Kelola Akun Karyawan"],
            ["4", "Lihat Laporan Produksi"],
            ["5", "Kelola Transaksi Pelanggan"],
            ["6", "Pergantian Manager Baru"],
            ["7", "Logout"]
        ]

        print("=== Halaman Menu Manajer Produksi ===")
        print(tabulate(menu, headers=["No", "Menu"], tablefmt="fancy_grid"))

        try:
            pilihan_mgr = int(input("Pilih menu: "))
        except ValueError:
            print("Input harus berupa angka, coba lagi.")
            continue

        if pilihan_mgr == 1:
            lihat_biodata_karyawan()
        elif pilihan_mgr == 2:
            edit_bio_karyawan()
        elif pilihan_mgr == 3:
            kelola_akun_karyawan()
        elif pilihan_mgr == 4:
            lihat_laporan_produksi()
        elif pilihan_mgr == 5:
            kelola_transaksi_pelanggan()
        elif pilihan_mgr == 6:
            ganti_mgr_baru()
        elif pilihan_mgr == 7:
            logout()
            exit()
        else:
            print("Pilihan tidak valid, coba lagi.")

def kelola_akun_karyawan():
    while True:
        print("\n=== Kelola Akun Karyawan ===")
        print("1. Lihat Karyawan")
        print("2. Tambah Karyawan")
        print("3. Edit Karyawan")
        print("4. Hapus Karyawan")
        print("5. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            lihat_karyawan()
        elif pilihan == "2":
            tambah_karyawan()
        elif pilihan == "3":
            edit_karyawan()
        elif pilihan == "4":
            hapus_karyawan()
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid!")

def lihat_karyawan():
    conn, cur = connectDB()
    if not conn: 
        return
    
    cur.execute("SELECT * FROM karyawan")
    data = cur.fetchall()
    
    if data:
        print("\n=== Daftar Karyawan ===")
        headers = [desc[0] for desc in cur.description]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("Belum ada data karyawan.")
    
    cur.close()
    conn.close()

def tambah_karyawan():
    conn, cur = connectDB()
    if not conn: return

    nama = input("Nama: ")
    username = input("Username: ")
    sandi = input("Password: ")
    gender_input = int(input("Gender (1. Perempuan / 0. Laki-laki): "))
    gender = True if gender_input == 1 else False
    status_input = int(input("Status (1. Aktif / 0. Nonaktif): "))
    status = True if status_input == 1 else False
    tgl_lahir = input("Tanggal Lahir (YYYY-MM-DD): ")
    no_telp = input("No Telepon: ")
    id_jabatan = input("ID Jabatan (2. Admin Produksi/ 3. Admin Gudang): ")
    gaji = int(input("Gaji: "))

    cur.execute("""
    INSERT INTO karyawan 
    (nama_karyawan, username_karyawan, kata_sandi_karyawan, gender, status_karyawan, tgl_lahir, no_telp, tgl_masuk, id_jabatan, gaji_karyawan)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (nama, username, sandi, gender, status, tgl_lahir, no_telp, datetime.now().date(), id_jabatan, gaji))
    conn.commit()
    print("Karyawan berhasil ditambahkan.")
    cur.close(); conn.close()

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

def ganti_mgr_baru():
    print("=== Ganti Manager Baru ===")
    conn, cur = connectDB()
    if not conn: return

    username_karyawan = input("Masukkan username manager lama: ")

    query = "SELECT * FROM karyawan WHERE username_karyawan = %s"
    cur.execute(query, (username_karyawan,))
    result = cur.fetchone()

    if result:
        nama_baru = input("Nama Manager Baru: ")
        gender = int(input("Gender (1. Perempuan / 0. Laki-laki): "))
        gender_baru = True if gender == 1 else False
        tgl_lahir_baru = input("Tgl Lahir (YYYY-MM-DD): ")
        no_telp_baru = input("No Telepon: ")
        tgl_masuk_baru = datetime.now().date()

        update_query = """
            UPDATE karyawan 
            SET nama_karyawan = %s, gender = %s, tgl_lahir = %s, no_telp = %s, tgl_masuk = %s
            WHERE username_karyawan = %s
        """
        cur.execute(update_query, (nama_baru, gender_baru, tgl_lahir_baru, no_telp_baru, tgl_masuk_baru, username_karyawan))
        conn.commit()
        print("Manager baru berhasil diganti. Tanggal masuk otomatis diisi hari ini.")
    else:
        print("Data manager tidak ditemukan.")

    cur.close()
    conn.close()

def kelola_transaksi_pelanggan():
    while True:
        print("\n=== Kelola Transaksi Pelanggan ===")
        print("1. Lihat Transaksi")
        print("2. Lihat Riwayat Transaksi")
        print("3. Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            lihat_transaksi()
        elif pilihan == "2":
            lihat_riwayat_transaksi()
        elif pilihan == "3":
            break
        else:
            print("Pilihan tidak valid.")

def lihat_transaksi():
    print("=== Lihat Transaksi ===")
    conn, cur = connectDB()
    if not conn: 
        return

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
        print("\n=== Daftar Transaksi ===")
        headers = ['ID Transaksi', 'Tanggal', 'Jenis Produk', 
                   'Jumlah', 'Harga Satuan', 'Subtotal', 'Status']
        print(tabulate(result, headers=headers, tablefmt="fancy_grid"))
    else:
        print("Transaksi tidak ditemukan.")
    cur.close()
    conn.close()

def lihat_riwayat_transaksi():
    print("=== Lihat Riwayat Transaksi ===")
    conn, cur = connectDB()
    if not conn: return

    query = """
    SELECT 
        t.id_transaksi, t.tgl_transaksi, jp.nama_jenis AS jenis_produk, dt.quantity, jp.harga_produk,
        (dt.quantity * jp.harga_produk) AS subtotal, pl.nama_pelanggan, mp.nama_transaksi, st.nama_status
    FROM transaksi t
    JOIN detail_transaksi dt ON t.id_transaksi = dt.id_transaksi
    JOIN produk p ON dt.id_produk = p.id_produk
    JOIN jenis_produk jp ON p.id_jenis_produk = jp.id_jenis_produk
    JOIN status_transaksi st ON t.id_status_transaksi = st.id_status_transaksi
    JOIN pelanggan pl ON t.id_pelanggan = pl.id_pelanggan
    JOIN metode_pembayaran mp ON t.id_metode_pembayaran = mp.id_metode_pembayaran
    WHERE st.nama_status = 'selesai'
    ORDER BY t.tgl_transaksi DESC
"""
    cur.execute(query)
    data = cur.fetchall()

    if data:
        print("\n=== Daftar Riwayat Transaksi ===")
        headers = ["ID Transaksi", "Tanggal", "Jenis Produk", "Jumlah", 
                   "Harga Satuan", "Subtotal", "Nama Pelanggan", 
                   "Metode Pembayaran", "Status"]
        print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("Belum ada riwayat transaksi dengan status 'selesai'.")

    cur.close()
    conn.close()

main()