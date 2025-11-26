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
# Pastikan API KEY sudah ada di Variables Railway
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

        # 3. Prompt Engineering yang Lebih Spesifik & Panjang
        # Kita minta AI fokus pada 3 elemen tari: Wiraga (Raga), Wirama (Irama), Wirasa (Rasa)
        prompt_text = (
            f"Berikan {feedback_num} poin evaluasi teknis yang mendalam (minimal 2-3 kalimat per poin) "
            "untuk seorang penari tari tradisional Indonesia. "
            "Bayangkan kamu adalah juri kompetisi tari yang sangat detail. "
            "Gunakan istilah teknis seperti 'mendak' (rendahkan badan), 'ngiting' (posisi jari), "
            "'seblak' (gerakan selendang/tangan), 'power', atau 'fokus mata'.\n\n"
            "Kritisi aspek berikut secara acak namun tajam:\n"
            "- Wiraga: Detail kelenturan jari, posisi bahu yang tidak boleh naik, dan kuda-kuda kaki.\n"
            "- Wirama: Ketepatan perpindahan gerak dengan aksen musik.\n"
            "- Wirasa: Ekspresi wajah (senyum/tegas) dan nyawa tarian.\n\n"
            "Format output: Hanya daftar kalimat evaluasi yang dipisahkan baris baru (newline), "
            "tanpa nomor (1, 2, 3) dan tanpa tanda bullet (-)."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini", # Menggunakan model yang pintar tapi cepat
            messages=[
                {
                    "role": "system", 
                    "content": "Kamu adalah pakar tari tradisional Indonesia yang perfeksionis, tegas, namun membangun."
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7, # Sedikit lebih rendah agar kalimatnya terstruktur rapi tapi tetap variatif
        )

        # 4. Parsing hasil
        raw_content = response.choices[0].message.content.strip()
        
        # Membersihkan hasil jika AI masih bandel kasih nomor atau bullet
        feedback_list = []
        for line in raw_content.split('\n'):
            clean_line = line.strip()
            # Hapus angka di depan (misal "1. ") atau bullet ("- ")
            if clean_line:
                if clean_line[0].isdigit():
                    clean_line = clean_line.split('.', 1)[-1].strip()
                if clean_line.startswith('- '):
                    clean_line = clean_line[2:]
                feedback_list.append(clean_line)

        # Ambil sesuai jumlah yang diminta (jaga-jaga AI generate kebanyakan)
        selected_feedback = feedback_list[:feedback_num]

        return {
            "feedback_num": len(selected_feedback),
            "feedback": selected_feedback,
            "score": score
        }

    except Exception as e:
        print(f"Error: {e}")
        # Fallback jika OpenAI error
        fallback_feedback = [
            "Posisi mendak kamu perlu diperbaiki, cobalah untuk menurunkan pusat berat badan lebih rendah lagi agar kuda-kuda terlihat kokoh dan tidak goyah saat perpindahan kaki.",
            "Gerakan ngiting pada jari-jari tanganmu sudah mulai terlihat bentuknya, namun perlu tenaga ekstra di ujung jari agar lentik dan tidak terlihat layu.",
            "Perhatikan aksen musik pada bagian transisi, kamu sedikit terlambat masuk ke gerakan berikutnya sehingga wirama terasa kurang sinkron dengan gamelan.",
            "Ekspresi wajah atau wirasa masih terlihat kosong, cobalah untuk memancarkan senyum yang berasal dari mata (eye contact) agar tarian lebih hidup.",
            "Gerakan bahu harus tetap rileks dan turun, jangan sampai terbawa naik saat mengangkat tangan karena itu merusak garis estetika tubuh."
        ]
        return {
            "feedback_num": 5,
            "feedback": fallback_feedback,
            "score": random.randint(75, 85)
        }

@app.get("/")
def read_root():
    return {"status": "Updated API is running. Hit /api/givescore to test."}