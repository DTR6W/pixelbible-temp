import sys, subprocess, os
sys.argv = ["build5.py", "genesis", "nar", "none"]
exec(open("build5.py").read().split('if STAGE == "preview"')[0])
FPSV = FPS
ranges = [(412.1, 492.4), (1093.4, 1146.6)]
for k, (a, b) in enumerate(ranges):
    out = f"{OUTD}/patch{k}.mp4"
    p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-crf","19","-preset","veryfast","-pix_fmt","yuv420p",out], stdin=subprocess.PIPE)
    for i in range(int(a*FPS), int(b*FPS)): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print("patch", k, flush=True)
# overlay patches onto the existing video, re-encode once
fc = "[0:v]"
ins = ["-i", f"{OUTD}/video.mp4"]
for k, (a, b) in enumerate(ranges): ins += ["-i", f"{OUTD}/patch{k}.mp4"]
parts = []; last = "[0:v]"
for k, (a, b) in enumerate(ranges):
    parts.append(f"[{k+1}:v]setpts=PTS-STARTPTS+{a}/TB[p{k}]")
    parts.append(f"{last}[p{k}]overlay=enable='between(t,{a},{b})':eof_action=pass[o{k}]"); last = f"[o{k}]"
subprocess.run(["ffmpeg","-y","-loglevel","error"]+ins+["-filter_complex",";".join(parts),"-map",last,"-c:v","libx264","-crf","19","-preset","veryfast","-pix_fmt","yuv420p",f"{OUTD}/video2.mp4"],check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{OUTD}/video2.mp4","-i",f"{OUTD}/mix.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",f"{OUTD}/genesis_nar_v2.mp4"],check=True)
print("PATCHDONE")
