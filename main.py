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
        # 1. Tentukan jumlah feedback/poin penilaian (5 - 7 poin)
        feedback_num = random.randint(5, 7)

        # 2. Generate Array Score sesuai jumlah feedback
        # Setiap poin feedback akan memiliki skor masing-masing (70-95)
        scores_array = [random.randint(70, 95) for _ in range(feedback_num)]

        # 3. Hitung Average Score
        # Rumus: Total Score / Jumlah Data, dibulatkan 1 desimal
        average_score = round(sum(scores_array) / feedback_num, 1)

        # 4. Prompt Engineering (Tetap Tari Lenggang Nyai)
        prompt_text = (
            f"Berikan {feedback_num} poin evaluasi teknis singkat (1-2 kalimat per poin) "
            "untuk penari Tari Lenggang Nyai (Betawi) berdasarkan deteksi pose tubuh (tanpa wajah). "
            "Setiap poin mewakili penilaian untuk satu segmen gerakan. "
            "Fokus pada: keluwesan pinggul, kewer tangan, kuda-kuda (mendak), dan power hentakan kaki. "
            "Output: Hanya daftar kalimat dipisahkan baris baru."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Kamu adalah juri tari Betawi yang memberikan catatan teknis per segmen gerakan."
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
        )

        # 5. Parsing hasil OpenAI
        raw_content = response.choices[0].message.content.strip()
        
        feedback_list = []
        for line in raw_content.split('\n'):
            clean_line = line.strip()
            if clean_line:
                # Bersihkan angka atau bullet di awal kalimat
                if clean_line[0].isdigit():
                    clean_line = clean_line.split('.', 1)[-1].strip()
                if clean_line.startswith('- '):
                    clean_line = clean_line[2:]
                feedback_list.append(clean_line)

        # Pastikan jumlah feedback sama dengan jumlah score
        # (Ambil slice jika AI generate kelebihan, atau biarkan jika kurang - idealnya match)
        selected_feedback = feedback_list[:feedback_num]
        
        # Jaga-jaga kalau AI generate feedback lebih sedikit dari feedback_num (jarang terjadi),
        # kita potong array score biar panjangnya sama persis dengan feedback yg tersedia
        if len(selected_feedback) < feedback_num:
            actual_length = len(selected_feedback)
            scores_array = scores_array[:actual_length]
            feedback_num = actual_length
            # Hitung ulang average jika array berubah
            if actual_length > 0:
                average_score = round(sum(scores_array) / actual_length, 1)

        return {
            "feedback_num": feedback_num,
            "feedback": selected_feedback,  # List of Strings
            "score": scores_array,          # List of Integers (Baru)
            "average_score": average_score  # Float (Baru)
        }

    except Exception as e:
        print(f"Error: {e}")
        # Fallback Logic (Juga harus update struktur datanya)
        fallback_feedback = [
            "Gerakan pinggul kurang lepas saat goyang.",
            "Posisi tangan kewer masih kaku di pergelangan.",
            "Kuda-kuda mendak perlu lebih rendah lagi.",
            "Koordinasi kaki terlambat dengan tempo musik.",
            "Bahu sering terangkat, harusnya rileks."
        ]
        # Generate score array untuk fallback (panjang 5)
        fallback_scores = [random.randint(75, 85) for _ in range(5)]
        fallback_avg = round(sum(fallback_scores) / 5, 1)

        return {
            "feedback_num": 5,
            "feedback": fallback_feedback,
            "score": fallback_scores,      # Array
            "average_score": fallback_avg  # Float
        }

@app.get("/")
def read_root():
    return {"status": "API Updated: Score is now an Array with Average."}