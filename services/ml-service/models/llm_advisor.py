import os
import requests
from config import config

class LLMAdvisor:
    """
    LLM Diagnostic Advisor module using Google Gemini API.
    Provides natural language explanations and technical recommendations for IoT anomalies.
    """
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY

    def explain_anomaly(self, device_name: str, sensor_name: str, value: float, unit: str, reason: str) -> str:
        if not self.api_key:
            return f"[LLM Advisor] GEMINI_API_KEY tidak dikonfigurasi. Deteksi teknis: {reason} pada nilai {value} {unit}."

        prompt = f"""
        Anda adalah Sistem AI Pakar IoT dan Pemeliharaan Industri (IoT Industrial Expert).
        Terdeteksi anomali pada sistem monitoring IoT:
        - Nama Perangkat: {device_name}
        - Nama Sensor: {sensor_name}
        - Nilai Terbaca saat ini: {value} {unit}
        - Alasan Anomali: {reason}

        Berikan analisis singkat (maksimal 3 kalimat) dalam bahasa Indonesia yang mencakup:
        1. Kemungkinan masalah fisik/teknis yang terjadi.
        2. Rekomendasi langkah mitigasi/perbaikan langsung untuk teknisi/operator.
        """

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            else:
                return f"[LLM Advisor] Gagal memanggil LLM API (Status: {response.status_code}). Alasan Anomali: {reason}"
        except Exception as e:
            return f"[LLM Advisor Error] {str(e)}. Alasan Anomali: {reason}"
