import os
import random
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI

app = FastAPI()

# --- KONFIGURASI CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SETUP OPENAI ---
# Kita ambil API KEY dari Environment Variable (Setting di Railway)
# Ini jauh lebih aman daripada menaruhnya langsung di kodingan.
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY") 
)

# --- ENDPOINT UTAMA ---
@app.api_route("/api/givescore", methods=["GET", "POST"])
async def give_score():
    try:
        # 1. Generate Fake Score (70 - 95)
        score = random.randint(70, 95)

        # 2. Tentukan jumlah feedback (5 - 7 poin)
        feedback_num = random.randint(5, 7)

        # 3. Minta OpenAI buatkan Feedback Unik
        # Kita suruh AI berperan sebagai pelatih tari
        prompt_text = (
            f"Berikan {feedback_num} poin masukan singkat (maksimal 10-15 kata per poin) "
            "untuk seorang penari tari tradisional Indonesia pemula setelah melakukan latihan. "
            "Variasikan komentar mengenai: keluwesan tangan, power/tenaga, ekspresi wajah, "
            "kuda-kuda kaki, dan ketepatan dengan musik. "
            "Berikan campuran pujian dan koreksi. "
            "Output hanya berupa daftar kalimat dipisahkan dengan baris baru (newline), tanpa penomoran."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini", # Atau "gpt-3.5-turbo" agar lebih hemat
            messages=[
                {"role": "system", "content": "Kamu adalah instruktur tari profesional yang ramah namun teliti."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.8, # Agar variasi kalimatnya tinggi (tidak monoton)
        )

        # 4. Parsing hasil dari OpenAI menjadi List
        raw_content = response.choices[0].message.content.strip()
        
        # Pisahkan berdasarkan baris baru dan bersihkan jika ada string kosong
        feedback_list = [line.strip("- ").strip() for line in raw_content.split('\n') if line.strip()]

        # Jaga-jaga kalau AI generate format aneh, kita potong sesuai feedback_num
        selected_feedback = feedback_list[:feedback_num]

        # 5. Return JSON
        return {
            "feedback_num": len(selected_feedback),
            "feedback": selected_feedback,
            "score": score
        }

    except Exception as e:
        print(f"Error: {e}")
        # Fallback jika OpenAI error/habis kuota, tetap return data dummy agar frontend tidak crash
        fallback_feedback = [
            "Gerakan tangan kamu sudah cukup luwes.",
            "Sinkronisasi dengan ketukan musik sangat pas.",
            "Perhatikan kuda-kuda kaki agar lebih kokoh.",
            "Ekspresi wajah perlu lebih menjiwai lagi.",
            "Power pada hentakan tangan perlu ditambah sedikit."
        ]
        return {
            "feedback_num": 5,
            "feedback": fallback_feedback,
            "score": random.randint(70, 85)
        }

@app.get("/")
def read_root():
    return {"status": "Server running with OpenAI integration."}