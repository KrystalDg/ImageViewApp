from tkinter.messagebox import showerror

import mysql.connector

cmc_query = """CREATE TABLE cmc_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                quyetDinhSo VARCHAR(50),
                ngayDangKy VARCHAR(50),
                loaiDangKy VARCHAR(50),
                loaiXacNhan VARCHAR(50),
                noiDangKy VARCHAR(50),
                nguoiKy VARCHAR(50),
                chucVuNguoiKy VARCHAR(50),
                nguoiThucHien VARCHAR(50),
                ghiChu VARCHAR(50),
                cmHoTen VARCHAR(50),
                cmGioiTinh VARCHAR(50),
                cmNgaySinh VARCHAR(50),
                cmDanToc VARCHAR(50),
                cmQuocTich VARCHAR(50),
                cmQuocTichKhac VARCHAR(50),
                cmQueQuan VARCHAR(50),
                cmLoaiCuTru VARCHAR(50),
                cmNoiCuTru VARCHAR(50),
                cmLoaiGiayToTuyThan VARCHAR(50),
                cmGiayToKhac VARCHAR(50),
                cmSoGiayToTuyThan VARCHAR(50),
                cmNgayCapGiayToTuyThan VARCHAR(50),
                cmNoiCapGiayToTuyThan VARCHAR(50),
                ncHoTen VARCHAR(50),
                ncGioiTinh VARCHAR(50),
                ncNgaySinh VARCHAR(50),
                ncDanToc VARCHAR(50),
                ncQuocTich VARCHAR(50),
                ncQuocTichKhac VARCHAR(50),
                ncQueQuan VARCHAR(50),
                ncLoaiCuTru VARCHAR(50),
                ncNoiCuTru VARCHAR(50),
                ncLoaiGiayToTuyThan VARCHAR(50),
                ncGiayToKhac VARCHAR(50),
                ncSoGiayToTuyThan VARCHAR(50),
                ncNgayCapGiayToTuyThan VARCHAR(50),
                ncNoiCapGiayToTuyThan VARCHAR(50),
                nycHoTen VARCHAR(50),
                nycQHNguoiDuocNhan VARCHAR(50),
                nycQHNguoiNhan VARCHAR(50),
                nycLoaiGiayToTuyThan VARCHAR(50),
                nycGiayToKhac VARCHAR(50),
                nycSoGiayToTuyThan VARCHAR(50),
                nycNgayCapGiayToTuyThan VARCHAR(50),
                nycNoiCapGiayToTuyThan VARCHAR(50),
                soDangKyNuocNgoai VARCHAR(50),
                ngayDangKyNuocNgoai VARCHAR(50),
                cqNuocNgoaiDaDangKy VARCHAR(50),
                qgNuocNgoaiDaDangKy VARCHAR(50),
                dataFilePath VARCHAR(50)
            )"""
kh_query = """CREATE TABLE kh_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                STT VARCHAR(50),
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                ngayDangKy VARCHAR(50),
                loaiDangKy VARCHAR(50),
                noiDangKy VARCHAR(50),
                nguoiKy VARCHAR(50),
                chucVuNguoiKy VARCHAR(50),
                ngayXacLapQuanHeHonNhan VARCHAR(50),
                nguoiThucHien VARCHAR(50),
                ghiChu VARCHAR(50),
                tinhTrangKetHon VARCHAR(50),
                huyKetHonNgayGhiChu VARCHAR(50),
                huyKetHonCanCu VARCHAR(50),
                congNhanKetHonNgayGhiChu VARCHAR(50),
                congNhanKetHonCanCu VARCHAR(50),
                chongHoTen  VARCHAR(50),
                chongNgaySinh VARCHAR(50),
                chongDanToc  VARCHAR(50),
                chongQuocTich  VARCHAR(50),
                chongQuocTichKhac VARCHAR(50),
                chongLoaiCuTru VARCHAR(50),
                chongNoiCuTru VARCHAR(50),
                chongLoaiGiayToTuyThan VARCHAR(50),
                chongGiayToKhac VARCHAR(50),
                chongSoGiayToTuyThan  VARCHAR(50),
                chongNgayCapGiayToTuyThan VARCHAR(50),
                chongNoiCapGiayToTuyThan VARCHAR(50),
                voHoTen  VARCHAR(50),
                voNgaySinh VARCHAR(50),
                voDanToc  VARCHAR(50),
                voQuocTich  VARCHAR(50),
                voQuocTichKhac VARCHAR(50),
                voLoaiCuTru VARCHAR(50),
                voNoiCuTru VARCHAR(50),
                voLoaiGiayToTuyThan VARCHAR(50),
                voGiayToKhac VARCHAR(50),
                voSoGiayToTuyThan  VARCHAR(50),
                voNgayCapGiayToTuyThan VARCHAR(50),
                voNoiCapGiayToTuyThan VARCHAR(50),
                soDangKyNuocNgoai VARCHAR(50),
                ngayDangKyNuocNgoai VARCHAR(50),
                cqNuocNgoaiDaDangKy VARCHAR(50),
                qgNuocNgoaiDaDangKy VARCHAR(50),
                dataFilePath VARCHAR(50)
            )"""
hn_query = """CREATE TABLE hn_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                STT VARCHAR(50),
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                ngayDangKy VARCHAR(50),
                noiCap  VARCHAR(50),
                nguoiKy VARCHAR(50),
                chucVuNguoiKy VARCHAR(50),
                nguoiThucHien VARCHAR(50),
                ghiChu VARCHAR(50),
                nxnHoTen  VARCHAR(50),
                nxnGioiTinh  VARCHAR(50),
                nxnNgaySinh VARCHAR(50),
                nxnDanToc  VARCHAR(50),
                nxnQuocTich  VARCHAR(50),
                nxnQuocTichKhac VARCHAR(50),
                nxnLoaiCuTru VARCHAR(50),
                nxnNoiCuTru VARCHAR(50),
                nxnLoaiGiayToTuyThan VARCHAR(50),
                nxnGiayToKhac VARCHAR(50),
                nxnSoGiayToTuyThan VARCHAR(50),
                nxnNgayCapGiayToTuyThan VARCHAR(50),
                nxnNoiCapGiayToTuyThan VARCHAR(50),
                nxnThoiGianCuTruTai VARCHAR(50),
                nxnThoiGianCuTruTu VARCHAR(50),
                nxnThoiGianCuTruDen VARCHAR(50),
                nxnTinhTrangHonNhan  VARCHAR(50),
                nxnLoaiMucDichSuDung  VARCHAR(50),
                nxnMucDichSuDung  VARCHAR(50),
                nycHoTen VARCHAR(50),
                nycQuanHe VARCHAR(50),
                nycLoaiGiayToTuyThan VARCHAR(50),
                nycGiayToKhac VARCHAR(50),
                nycSoGiayToTuyThan VARCHAR(50),
                nycNgayCapGiayToTuyThan VARCHAR(50),
                nycNoiCapGiayToTuyThan VARCHAR(50),
                dataFilePath VARCHAR(50)
            )"""
ks_query = """CREATE TABLE ks_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                STT VARCHAR(50),
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                ngayDangKy VARCHAR(50),
                loaiDangKy  VARCHAR(50),
                noiDangKyUBND VARCHAR(50),
                nguoiKy VARCHAR(50),
                chucVuNguoiKy VARCHAR(50),
                nguoiThucHien VARCHAR(50),
                ghiChu VARCHAR(50),
                nksHoTen   VARCHAR(50),
                nksGioiTinh  VARCHAR(50),
                nksNgaySinh VARCHAR(50),
                nksNgaySinhBangChu VARCHAR(50),
                nksNoiSinh VARCHAR(50),
                nksNoiSinhDVHC VARCHAR(50),
                nksQueQuan VARCHAR(50),
                nksDanToc  VARCHAR(50),
                nksQuocTich  VARCHAR(50),
                nksQuocTichKhac VARCHAR(50),
                nksLoaiKhaiSinh VARCHAR(50),
                nksMatTich VARCHAR(50),
                nksMatTichNgayGhiChuTuyenBo VARCHAR(50),
                nksMatTichCanCuTuyenBo VARCHAR(50),
                nksMatTichNgayGhiChuHuyTuyenBo VARCHAR(50),
                nksMatTichCanCuHuyTuyenBo VARCHAR(50),
                nksHanCheNangLucHanhVi VARCHAR(50),
                nksHanCheNangLucHanhViNgayGhiChuTuyenBo VARCHAR(50),
                nksHanCheNangLucHanhViCanCuTuyenBo VARCHAR(50),
                nksHanCheNangLucHanhViNgayGhiChuHuyTuyenBo VARCHAR(50),
                nksHanCheNangLucHanhViNgayCanCuHuyTuyenBo  VARCHAR(50),
                meHoTen VARCHAR(50),
                meNgaySinh  VARCHAR(50),
                meDanToc  VARCHAR(50),
                meQuocTich  VARCHAR(50),
                meQuocTichKhac VARCHAR(50),
                meLoaiCuTru  VARCHAR(50),
                meNoiCuTru VARCHAR(50),
                meLoaiGiayToTuyThan VARCHAR(50),
                meSoGiayToTuyThan VARCHAR(50),
                chaHoTen VARCHAR(50),
                chaNgaySinh VARCHAR(50),
                chaDanToc  VARCHAR(50),
                chaQuocTich  VARCHAR(50),
                chaQuocTichKhac VARCHAR(50),
                chaLoaiCuTru  VARCHAR(50),
                chaNoiCuTru VARCHAR(50),
                chaLoaiGiayToTuyThan VARCHAR(50),
                chaSoGiayToTuyThan VARCHAR(50),
                nycHoTen VARCHAR(50),
                nycQuanHe VARCHAR(50),
                nycLoaiGiayToTuyThan VARCHAR(50),
                nycGiayToKhac VARCHAR(50),
                nycSoGiayToTuyThan VARCHAR(50),
                nycNgayCapGiayToTuyThan VARCHAR(50),
                nycNoiCapGiayToTuyThan VARCHAR(50),
                soDangKyNuocNgoai VARCHAR(50),
                ngayDangKyNuocNgoai VARCHAR(50),
                cqNuocNgoaiDaDangKy VARCHAR(50),
                qgNuocNgoaiDaDangKy VARCHAR(50),
                dataFilePath VARCHAR(50)
            )"""
kt_query = """CREATE TABLE kt_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                STT VARCHAR(50),
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                ngayDangKy VARCHAR(50),
                loaiDangKy  VARCHAR(50),
                noiDangKyUBND VARCHAR(50),
                nguoiKy VARCHAR(50),
                chucVuNguoiKy VARCHAR(50),
                nguoiThucHien VARCHAR(50),
                ghiChu VARCHAR(50),
                nktHoTen VARCHAR(50),
                nktGioiTinh VARCHAR(50),
                nktNgaySinh VARCHAR(50),
                nktDanToc VARCHAR(50),
                nktQuocTich VARCHAR(50),
                nktQuocTichKhac VARCHAR(50),
                nktLoaiCuTru VARCHAR(50),
                nktNoiCuTru VARCHAR(50),
                nktLoaiGiayToTuyThan VARCHAR(50),
                nktGiayToKhac VARCHAR(50),
                nktSoGiayToTuyThan  VARCHAR(50),
                nktNgayCapGiayToTuyThan VARCHAR(50),
                nktNoiCapGiayToTuyThan VARCHAR(50),
                nktNgayChet VARCHAR(50),
                nktGioPhutChet VARCHAR(50),
                nktNoiChet VARCHAR(50),
                nktNguyenNhanChet VARCHAR(50),
                nktTinhTrangTuyenBoViecChet VARCHAR(50),
                nktNgayGhiChuTuyenBoViecChet VARCHAR(50),
                nktCanCuTuyenBoViecChet VARCHAR(50),
                nktNgayGhiChuHuyTuyenBoViecChet VARCHAR(50),
                nktCanCuHuyTuyenBoViecChet VARCHAR(50),
                gbtLoai VARCHAR(50),
                gbtSo VARCHAR(50),
                gbtNgay VARCHAR(50),
                gbtCoQuanCap VARCHAR(50),
                nycHoTen VARCHAR(50),
                nycQuanHe VARCHAR(50),
                nycLoaiGiayToTuyThan VARCHAR(50),
                nycGiayToKhac VARCHAR(50),
                nycSoGiayToTuyThan VARCHAR(50),
                nycNgayCapGiayToTuyThan VARCHAR(50),
                nycNoiCapGiayToTuyThan VARCHAR(50),
                soDangKyNuocNgoai VARCHAR(50),
                ngayDangKyNuocNgoai VARCHAR(50),
                cqNuocNgoaiDaDangKy VARCHAR(50),
                qgNuocNgoaiDaDangKy VARCHAR(50),
                dataFilePath VARCHAR(50)
            )"""
ht_query = """CREATE TABLE ht_form(
                id INT AUTO_INCREMENT PRIMARY KEY,
                STT VARCHAR(50),
                so VARCHAR(50),
                quyenSo VARCHAR(50),
                trangSo VARCHAR(50),
                nksHoTen VARCHAR(50),
                nksGioiTinh VARCHAR(50),
                nksNgaySinh VARCHAR(50),
                nksNoiSinh VARCHAR(50),
                nksQueQuan VARCHAR(50),
                nksDanToc VARCHAR(50),
                nksQuocTich VARCHAR(50),
                meHoTen VARCHAR(50),
                meNgaySinh VARCHAR(50),
                meNoiSinh VARCHAR(50),
                meQueQuan VARCHAR(50),
                meDanToc VARCHAR(50),
                meQuocTich VARCHAR(50),
                boHoTen VARCHAR(50),
                boNgaySinh VARCHAR(50),
                boNoiSinh VARCHAR(50),
                boQueQuan VARCHAR(50),
                boDanToc VARCHAR(50),
                boQuocTich VARCHAR(50)
            )"""


def initialize_connection():
    conn = None
    isConnect = False
    try:
        # Kết nối đến cơ sở dữ liệu MySQL
        conn = mysql.connector.connect(
            host="localhost", user="root", password="minh", database="lvtn_hk231"
        )
        isConnect = True
        print("Database Connected")
    except:
        print("Error")

    if isConnect:
        cursor = conn.cursor()
        create_database(cursor)
        create_table(cursor)

        return conn, cursor


def create_database(cursor):
    cursor.execute("SHOW DATABASES")
    temp = cursor.fetchall()
    databases = [item[0] for item in temp]

    if "lvtn_hk231" not in databases:
        cursor.execute("CREATE DATABASE lvtn_hk231")

    cursor.execute("USE lvtn_hk231")


def get_tables(cursor):
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]
    return tables


def create_table(cursor):
    tables = get_tables(cursor)

    if "cmc_form" not in tables:
        cursor.execute(cmc_query)
    else:
        cursor.execute("DROP TABLE cmc_form")
        cursor.execute(cmc_query)

    if "kh_form" not in tables:
        cursor.execute(kh_query)
    else:
        cursor.execute("DROP TABLE kh_form")
        cursor.execute(kh_query)

    if "hn_form" not in tables:
        cursor.execute(hn_query)
    else:
        cursor.execute("DROP TABLE hn_form")
        cursor.execute(hn_query)

    if "ks_form" not in tables:
        cursor.execute(ks_query)
    else:
        cursor.execute("DROP TABLE ks_form")
        cursor.execute(ks_query)

    if "kt_form" not in tables:
        cursor.execute(kt_query)
    else:
        cursor.execute("DROP TABLE kt_form")
        cursor.execute(kt_query)

    if "ht_form" not in tables:
        cursor.execute(ht_query)
    else:
        cursor.execute("DROP TABLE ht_form")
        cursor.execute(ht_query)


def get_table_header(cursor, table):
    cursor.execute(f"SHOW columns FROM {table}")
    headers = [column[0] for column in cursor.fetchall()]
    return headers


def submit(conn, cursor, table, col, row):
    try:
        query = f"INSERT INTO {table} ({col}) VALUES ({row})"
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        showerror("Error", f"Error submitting data: {str(e)}")
