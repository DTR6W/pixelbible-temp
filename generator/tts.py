import sys, soundfile as sf
from kokoro_onnx import Kokoro
S = sys.argv[1]
k = Kokoro(f"{S}/tts/kokoro-v1.0.onnx", f"{S}/tts/voices-v1.0.bin")
texts = {
 "intro": "Três fatos curiosos sobre o espaço. Fique até o final!",
 "f1": "Fato um. Em Vênus, um dia dura mais que um ano. O planeta leva cerca de duzentos e quarenta e três dias terrestres para girar uma vez, mas só duzentos e vinte e cinco para dar a volta no Sol.",
 "f2": "Fato dois. O Sol tem quase toda a massa do Sistema Solar. Cerca de noventa e nove vírgula oitenta e seis por cento. Todos os planetas juntos ficam com o resto.",
 "f3": "Fato três. A luz do Sol leva oito minutos para chegar até aqui. Mais exatamente, oito minutos e vinte segundos. Se o Sol sumisse agora, a gente só perceberia depois disso.",
 "outro": "Gostou? Segue o canal para mais curiosidades!",
}
import os; os.makedirs(f"{S}/audio", exist_ok=True)
for n, t in texts.items():
    x, sr = k.create(t, voice="pf_dora", speed=1.0, lang="pt-br")
    sf.write(f"{S}/audio/{n}.wav", x, sr)
    print(n, round(len(x)/sr, 2), "s", sr)
