import os
import random
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY") 
)

@app.api_route("/api/givescore", methods=["GET", "POST"])
async def give_score():
    try:
        # 1. Generate Fake Score (70 - 95)
        score = random.randint(70, 95)

        # 2. Tentukan jumlah feedback (5 - 7 poin)
        feedback_num = random.randint(5, 7)

        # 3. Prompt Engineering Spesifik Tari Lenggang Nyai (Tanpa Wajah)
        prompt_text = (
            f"Berikan {feedback_num} poin evaluasi teknis yang mendalam (minimal 2-3 kalimat per poin) "
            "untuk penari yang sedang melakukan Tari Lenggang Nyai (Betawi). "
            "Analisis didasarkan pada pose detection tubuh (body landmarks) tanpa melihat ekspresi wajah.\n\n"
            "Fokuskan kritik pada aspek gerakan fisik berikut:\n"
            "- Gerakan Pinggul: Keluwesan goyang pinggul yang menjadi ciri khas Lenggang Nyai (titik hip).\n"
            "- Gerakan Tangan: Keluwesan 'kewer' selendang dan ketegasan sudut siku serta pergelangan tangan (wrist & elbow).\n"
            "- Kuda-kuda (Mendak): Apakah posisi lutut cukup rendah dan kokoh atau terlalu kaku.\n"
            "- Energi/Power: Hentakan kaki dan ketegasan perpindahan gerak yang lincah.\n\n"
            "Gunakan istilah teknis tari seperti 'mendak', 'ngiting', 'kewer', atau 'tanjak'. "
            "Jangan berkomentar soal senyum atau lirikan mata karena tidak terdeteksi. "
            "Format output: Hanya daftar kalimat evaluasi dipisahkan baris baru."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Kamu adalah pelatih Tari Betawi profesional yang menilai berdasarkan data sensor gerak tubuh."
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
        )

        # 4. Parsing hasil
        raw_content = response.choices[0].message.content.strip()
        
        feedback_list = []
        for line in raw_content.split('\n'):
            clean_line = line.strip()
            # Bersihkan numbering/bullet jika AI tetap memberikannya
            if clean_line:
                if clean_line[0].isdigit():
                    clean_line = clean_line.split('.', 1)[-1].strip()
                if clean_line.startswith('- '):
                    clean_line = clean_line[2:]
                feedback_list.append(clean_line)

        selected_feedback = feedback_list[:feedback_num]

        return {
            "feedback_num": len(selected_feedback),
            "feedback": selected_feedback,
            "score": score
        }

    except Exception as e:
        print(f"Error: {e}")
        # Fallback Spesifik Tari Lenggang Nyai
        fallback_feedback = [
            "Gerakan pinggul kamu kurang lepas saat melakukan goyang, cobalah untuk lebih merelaksasi area pinggang agar gerakan terlihat luwes khas Betawi.",
            "Posisi tangan saat melakukan gerakan 'kewer' masih terlihat kaku di bagian pergelangan, pastikan jari-jari 'ngiting' dengan sempurna dan bertenaga.",
            "Perhatikan kuda-kuda (mendak) kamu, lutut perlu ditekuk sedikit lebih rendah lagi agar postur tubuh terlihat lebih membumi dan kokoh.",
            "Koordinasi antara langkah kaki dan ayunan tangan sedikit terlambat, pastikan hentakan kaki berbarengan dengan aksen musik yang dinamis.",
            "Bahu kamu terlihat sering terangkat saat tangan bergerak ke atas, usahakan bahu tetap rileks dan turun agar garis leher tetap terlihat jenjang."
        ]
        return {
            "feedback_num": 5,
            "feedback": fallback_feedback,
            "score": random.randint(75, 85)
        }

@app.get("/")
def read_root():
    return {"status": "Tari Lenggang Nyai API (No Face Detection) is running."}