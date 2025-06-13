
from IPython.display import display, Audio, clear_output
import ipywidgets as widgets
import requests, os, zipfile
from google.colab import files

# Gọi API ElevenLabs
def generate_voice(text, api_key, voice_id, stability, similarity, style, speed, speaker_boost):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    voice_settings = {
        "stability": float(stability),
        "similarity_boost": float(similarity),
        "style": float(style),
        "speed": float(speed),
        "use_speaker_boost": speaker_boost
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": voice_settings
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return res.content
    except Exception as e:
        print("Lỗi tạo giọng:", e)
    return None

def split_text(text, max_len=2500):
    sentences = text.split(".")
    blocks, current = [], ""
    for s in sentences:
        if len(current) + len(s) + 1 < max_len:
            current += s + "."
        else:
            blocks.append(current.strip())
            current = s + "."
    if current: blocks.append(current.strip())
    return blocks

def run_tool(api_bytes, voice_bytes, text_bytes, st, sm, sty, spd, boost):
    api_keys = [line.strip() for line in api_bytes.decode().splitlines() if line.strip()]
    voice_id = voice_bytes.decode().strip()
    text = text_bytes.decode()
    blocks = split_text(text)

    os.makedirs("voices", exist_ok=True)
    for i, t in enumerate(blocks):
        print(f"🔊 Đang tạo đoạn {i+1}/{len(blocks)}...")
        for key in api_keys:
            audio = generate_voice(t, key, voice_id, st, sm, sty, spd, boost)
            if audio:
                fname = f"voices/voice_{i+1:03}.mp3"
                with open(fname, "wb") as f:
                    f.write(audio)
                display(Audio(fname))
                break
        else:
            print(f"❌ Không thể tạo đoạn {i+1}")

    with zipfile.ZipFile("voices.zip", "w") as zipf:
        for f in os.listdir("voices"):
            zipf.write("voices/" + f)
    files.download("voices.zip")
    print("✅ Đã tạo xong tất cả và nén thành voices.zip")

# Giao diện
api_file = widgets.FileUpload(accept='.txt', multiple=False)
voice_file = widgets.FileUpload(accept='.txt', multiple=False)
text_file = widgets.FileUpload(accept='.txt', multiple=False)
stability = widgets.FloatSlider(value=0.7, min=0, max=1, step=0.05, description='Ổn định:')
similarity = widgets.FloatSlider(value=0.75, min=0, max=1, step=0.05, description='Giống giọng:')
style = widgets.FloatSlider(value=0.3, min=0, max=1, step=0.05, description='Phong cách:')
speed = widgets.FloatSlider(value=1.0, min=0.5, max=2, step=0.05, description='Tốc độ:')
boost = widgets.Checkbox(value=True, description="Tăng cường giọng")

btn = widgets.Button(description="🎧 Bắt đầu tạo giọng")
out = widgets.Output()

def on_click(b):
    with out:
        clear_output()
        try:
            run_tool(
                list(api_file.value.values())[0]['content'],
                list(voice_file.value.values())[0]['content'],
                list(text_file.value.values())[0]['content'],
                st=stability.value,
                sm=similarity.value,
                sty=style.value,
                spd=speed.value,
                boost=boost.value
            )
        except Exception as e:
            print("Lỗi:", e)

btn.on_click(on_click)

display(widgets.VBox([
    widgets.HTML("<h3>🔊 <b>VCHTTS Pro v2 – Tạo giọng nói tiếng Việt</b></h3><p>Tải 3 file: <code>api_keys.txt</code>, <code>voice_id.txt</code>, <code>texts.txt</code></p>"),
    api_file, voice_file, text_file,
    stability, similarity, style, speed, boost,
    btn, out
]))
