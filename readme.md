# Semarang Business Intelligence API 🚀

API ini merupakan *Decision Support System* berbasis Deep Learning (Multi-Output Neural Network) yang memprediksi potensi kesuksesan 12 jenis bisnis komersial di berbagai ruas jalan Kota Semarang.

Model ini mengevaluasi karakteristik spasial jalan (lalu lintas, infrastruktur, POI, dan *demand generator*) dan mengklasifikasikannya ke dalam tiga zona potensial: **Sepi (0)**, **Potensial (1)**, dan **Ramai (2)**.

---

## 🛠️ Bagian 1: Setup Server (Untuk AI/Backend Engineer)

Bagian ini berisi instruksi untuk menjalankan *server* inferensi secara lokal maupun di *cloud/VPS*.

### 1. Persyaratan File
Pastikan direktori proyek Anda memiliki struktur file berikut sebelum menyalakan server:
```text
├── main.py                             # Script FastAPI utama
├── model_multi_output_semarang.keras   # File model Deep Learning
├── scaler_semarang.pkl                 # File joblib StandardScaler (Penting!)
└── requirements.txt                    # Daftar library
```

### 2. Instalasi Dependensi
Sangat disarankan untuk menggunakan *Virtual Environment* (`venv` atau `conda`). Buka terminal dan jalankan:
```bash
pip install fastapi uvicorn tensorflow scikit-learn pydantic joblib pandas numpy
```

### 3. Menjalankan Server
Jalankan server menggunakan Uvicorn. Proses ini akan memuat model `.keras` ke dalam memori RAM (membutuhkan waktu beberapa detik).
```bash
uvicorn main:app --reload
```
* Server akan berjalan di: `http://127.0.0.1:8000`
* Dokumentasi interaktif (Swagger UI) otomatis tersedia di: `http://127.0.0.1:8000/docs`

---

## 💻 Bagian 2: API Documentation (Untuk Fullstack Developer)

Bagian ini adalah panduan integrasi untuk tim *Frontend/Fullstack* agar dapat mengirimkan data dari UI dan menerima hasil prediksi AI.

### Base URL
* **Local Development:** `http://127.0.0.1:8000`
* **Production:** `[URL_SERVER_PRODUCTION_ANDA]`

### Endpoint: Cek Status Server
Digunakan untuk memastikan *service* AI sedang menyala (cocok untuk *health-check ping*).
* **URL:** `/`
* **Method:** `GET`
* **Success Response:**
    ```json
    {
      "message": "AI Engine Online. Ready to scan Semarang City."
    }
    ```

### Endpoint: Prediksi Potensi 12 Bisnis
*Endpoint* utama yang memproses karakteristik ruas jalan dan mengembalikan probabilitas kesuksesan untuk 12 kategori bisnis sekaligus secara *real-time*.
* **URL:** `/predict`
* **Method:** `POST`
* **Headers:** `Content-Type: application/json`

#### Request Body (JSON)
Pastikan tipe datanya sesuai (angka desimal untuk `float`, angka bulat untuk `int`).
```json
{
  "panjang_m": 1250.5,
  "lebar_m": 6.0,
  "demand_university": 1,
  "demand_college": 0,
  "demand_school": 3,
  "demand_office": 2,
  "demand_mall": 0,
  "demand_hospital": 1,
  "traffic_score": 0.85,
  "total_poi_imputed": 12.5
}
```

#### Success Response (200 OK)
API akan merespons dengan objek JSON yang memetakan nasib 12 bisnis (`elektronik`, `fashion`, `laundry`, `photostudio`, `salon`, `carwash`, `stationery`, `cafe`, `barbershop`, `fnb`, `bengkel`, `gym`).

*Setiap bisnis akan memiliki:*
* `status`: Kesimpulan akhir (**Ramai / Potensial / Sepi**)
* `confidence`: Tingkat keyakinan model terhadap kesimpulan tersebut.
* `probabilities`: Rincian persentase lengkap untuk kebutuhan *chart/gauge meter* di UI.

```json
{
  "status": "success",
  "predictions": {
    "cafe": {
      "status": "Ramai",
      "confidence": "88.45%",
      "probabilities": {
        "Sepi": "2.10%",
        "Potensial": "9.45%",
        "Ramai": "88.45%"
      }
    },
    "laundry": {
      "status": "Potensial",
      "confidence": "65.20%",
      "probabilities": {
        "Sepi": "15.30%",
        "Potensial": "65.20%",
        "Ramai": "19.50%"
      }
    },
    "bengkel": {
      "status": "Sepi",
      "confidence": "92.11%",
      "probabilities": {
        "Sepi": "92.11%",
        "Potensial": "5.00%",
        "Ramai": "2.89%"
      }
    }
  }
}
```

### Catatan Penting untuk Fullstack:
1. **Validasi Input:** Jika ada parameter yang kurang atau tipe datanya salah (misal mengirimkan *string* huruf ke kolom `lebar_m`), FastAPI akan otomatis menolak dengan error `422 Unprocessable Entity`. Pastikan *form* di UI membatasi input hanya untuk angka.
2. **Visualisasi Rekomendasi:** Anda bisa menggunakan properti `status` untuk menentukan warna *marker* di peta (Misal: Ramai = Hijau, Potensial = Kuning, Sepi = Merah), dan menggunakan objek `probabilities` untuk menampilkan *pie chart* saat *user* mengklik detail jalan tersebut.