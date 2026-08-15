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

    def explain_anomaly(self, device_name: str, sensor_name: str, value: float, unit: str, reason: str) -> dict:
        fallback_res = {
            "problem": f"Nilai {sensor_name} terdeteksi tidak normal ({value} {unit}). Alasan: {reason}",
            "solution": "Periksa kondisi fisik perangkat dan kabel koneksi sensor."
        }

        if not self.api_key:
            return fallback_res

        prompt = f"""
        Anda adalah Sistem AI Pakar Pemeliharaan IoT.
        Terdeteksi anomali telemetri:
        - Perangkat: {device_name}
        - Sensor: {sensor_name}
        - Nilai Terbaca: {value} {unit}
        - Indikator Anomali: {reason}

        Berikan analisis terpisah yang ringkas dan mudah dibaca oleh operator.
        Keluarkan HANYA format JSON valid tanpa format markdown tambahan:
        {{
          "problem": "Penjelasan singkat (1-2 kalimat) mengenai potensi masalah fisik/teknis yang terjadi",
          "solution": "Langkah mitigasi/perbaikan langsung (1-2 kalimat) yang harus dilakukan teknisi"
        }}
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
                raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Bersihkan markdown codeblock jika ada
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                
                import json
                parsed_json = json.loads(raw_text.strip())
                return {
                    "problem": parsed_json.get("problem", fallback_res["problem"]),
                    "solution": parsed_json.get("solution", fallback_res["solution"])
                }
            else:
                return fallback_res
        except Exception as e:
            print(f"[ERROR] LLM Advisor Exception: {e}")
            return fallback_res
