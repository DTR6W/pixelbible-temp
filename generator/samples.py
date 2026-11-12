import sys, soundfile as sf
from kokoro_onnx import Kokoro
S = sys.argv[1]
k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
have = set(k.get_voices())
text = "Did you know the word Bible comes from the Greek word biblia, which simply means books? It is not one book, but a whole library of many."
for v, lang in (("af_heart","en-us"),("am_michael","en-us"),("am_adam","en-us"),("bm_george","en-gb"),("bf_emma","en-gb")):
    if v not in have: print("missing", v); continue
    x, sr = k.create(text, voice=v, speed=1.0, lang=lang)
    sf.write(f"{S}/samples/{v}.wav", x, sr); print(v, round(len(x)/sr,1))
