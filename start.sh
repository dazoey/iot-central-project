#!/bin/bash

echo "🚀 Memulai IoT Central Management System..."

# 1. Infrastruktur Docker
echo "📦 [1/4] Memulai infrastruktur Docker..."
docker-compose up -d

# 2. ML Service
echo "🧠 [2/4] Memulai Machine Learning Service..."
cd services/ml-service
if [ ! -d "venv" ]; then
    echo "⚠️ Virtual environment tidak ditemukan. Membuat venv dan menginstall dependensi..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi
./venv/bin/python3 main.py &
ML_PID=$!
cd ../..

# 3. Network Service
echo "⚡ [3/4] Memulai Network Protocol Service..."
cd services/network-service
rm -rf build && mkdir build && cd build
cmake .. > /dev/null && make > /dev/null
./network_service &
NET_PID=$!
cd ../../..

# 4. Backend Core
echo "⚙️ [4/4] Memulai Backend Core..."
cd apps/backend-core
if [ ! -d "node_modules" ]; then
    echo "⚠️ node_modules tidak ditemukan. Menjalankan npm install..."
    npm install
fi
npm start &
BACKEND_PID=$!
cd ../..

echo ""
echo "✅ Semua service berhasil dijalankan!"
echo "🛑 Tekan [CTRL+C] di terminal ini untuk menghentikan semua service sekaligus."
echo "=========================================================================="

# Cleanup function untuk menghentikan semuanya jika CTRL+C ditekan
cleanup() {
    echo ""
    echo "🛑 Menghentikan service-service lokal..."
    kill $ML_PID $NET_PID $BACKEND_PID 2>/dev/null
    
    echo "📦 Menghentikan Docker containers..."
    docker-compose stop
    
    echo "👋 Selesai!"
    exit 0
}

# Tangkap event CTRL+C
trap cleanup SIGINT SIGTERM

# Tunggu background process
wait $ML_PID $NET_PID $BACKEND_PID
