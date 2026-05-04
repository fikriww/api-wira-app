from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import joblib # Untuk memuat scaler jika disimpan terpisah

# 1. Inisialisasi App
app = FastAPI(
    title="Semarang Business Intelligence API",
    description="Multi-Output Model untuk memprediksi 12 jenis bisnis sekaligus",
    version="2.0.0"
)

# 2. Load Model & Custom Components
# Pastikan CustomDenseLayer disertakan agar model bisa terbaca
class CustomDenseLayer(tf.keras.layers.Layer):
    def __init__(self, units, activation=None, **kwargs):
        super(CustomDenseLayer, self).__init__(**kwargs)
        self.units = units
        self.activation = tf.keras.activations.get(activation)
    def build(self, input_shape):
        self.w = self.add_weight(shape=(input_shape[-1], self.units), initializer="glorot_uniform", trainable=True)
        self.b = self.add_weight(shape=(self.units,), initializer="zeros", trainable=True)
    def call(self, inputs):
        output = tf.matmul(inputs, self.w) + self.b
        return self.activation(output) if self.activation else output

# Load model
model = tf.keras.models.load_model(
    'model_multi_output_semarang.keras', 
    custom_objects={'CustomDenseLayer': CustomDenseLayer}
)

# Mapping Label (Sesuaikan dengan hasil mapping statistik deskriptif Anda)
CLASS_LABELS = {0: "Sepi", 1: "Potensial", 2: "Ramai"}
BUSINESS_TYPES = [
    'elektronik', 'fashion', 'laundry', 'photostudio', 'salon', 
    'carwash', 'stationery', 'cafe', 'barbershop', 'fnb', 'bengkel', 'gym'
]

# 3. Skema Input dari Fullstack
class StreetFeatures(BaseModel):
    # Masukkan semua fitur yang digunakan saat training (kecuali target)
    panjang_m: float
    lebar_m: float
    demand_university: int
    demand_college: int
    demand_school: int
    demand_office: int
    demand_mall: int
    demand_hospital: int
    traffic_score: float
    total_poi_imputed: float
    # Tambahkan fitur one-hot fungsi_jalan jika perlu, atau buat logic mapping di sini

# 4. Endpoint Prediksi
@app.post("/predict")
async def predict_business_potential(data: StreetFeatures):
    try:
        # 1. Persiapkan data numerik (10 fitur awal)
        features = [
            data.panjang_m, data.lebar_m, data.demand_university, data.demand_college,
            data.demand_school, data.demand_office, data.demand_mall, data.demand_hospital,
            data.traffic_score, data.total_poi_imputed
        ]

        # 2. Tambahkan placeholder untuk fitur sisa (one-hot encoding dll) hingga 33 fitur
        # Karena scaler/mapping lengkap tidak tersedia, kita gunakan padding 0
        current_len = len(features)
        target_len = 33
        if current_len < target_len:
            features.extend([0.0] * (target_len - current_len))
        
        input_data = np.array([features])

        # 3. Load Scaler jika tersedia (Opsional namun disarankan)
        try:
            scaler = joblib.load('scaler_semarang.pkl')
            input_data = scaler.transform(input_data)
        except:
            # Jika scaler tidak ada, gunakan data mentah (mungkin kurang akurat)
            pass


        # Prediksi sekaligus 12 output
        raw_predictions = model.predict(input_data)
        
        # Susun hasil akhir
        final_results = {}
        for biz in BUSINESS_TYPES:
            # Ambil output spesifik untuk bisnis tersebut
            output_key = f"output_{biz}"
            probs = raw_predictions[output_key][0]
            predicted_class = np.argmax(probs)
            
            final_results[biz] = {
                "status": CLASS_LABELS[predicted_class],
                "confidence": f"{np.max(probs) * 100:.2f}%",
                "probabilities": {CLASS_LABELS[i]: f"{probs[i]*100:.2f}%" for i in range(3)}
            }

        return {
            "status": "success",
            "predictions": final_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "AI Engine Online. Ready to scan Semarang City."}