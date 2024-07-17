import base64
import json
import pprint
import signal
from os import stat

import ggwave
import pyaudio
p = None
stream = None
instance = None


def handler(signum, frame):
    global p, stream, instance
    if instance is not None:
        ggwave.free(instance)

    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()
    exit(0)


signal.signal(signal.SIGINT, handler)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=4096)
# ggwave.disableLog()
print('Listening ... Press Ctrl+C to stop')
par = ggwave.getDefaultParameters()
# par["SampleRate"] = 44100
# par["SampleRateInp"] = 44100
# par["SampleRateOut"] = 44100
# par["Channels"] = 1
# par["Frequency"] = 44100
# par["SampleWidth"] = 8192
# par["SampleDepth"] = 8192
# par["SampleType"] = 2
# par["SampleChannels"] = 1
# par["SampleFrequency"] = 44100

instance = ggwave.init(par)
# pprint.pprint(ggwave.getDefaultParameters())
i = 0
started = False
pieces = 0
buf = ""
filename = None
size = 0

while True:
    data = stream.read(4096, exception_on_overflow=False)
    res = ggwave.decode(instance, data)
    if res is not None:
        try:
            st: str = res.decode("ascii")
            if st.startswith("{"):
                js = json.loads(st)
                # pieces = int(st.replace("Pieces: ", ""))
                pieces = js["pieces"]
                filename = js["filename"]
                size = js["size"]
                print(f"Filename: {filename}, Size: {size}")
                print(f"Piece {i}/{pieces}", end="\r", flush=True)
                started = True
            else:
                if i < pieces and started:
                    # print('Received text: ' + res.decode("utf-8"), "len:", len(res.decode("utf-8")))
                    buf += st
                    # print(part, end="", flush=True)
                    i += 1
                    print(f"Piece {i}/{pieces} {i*140} B", end="\r", flush=True)
                elif started:
                    break
        except Exception as e:
            pprint.pprint(e)
            pass
    if i >= pieces and started:
        # print()
        # print("*" * 30)
        if filename is not None:
            with open(f"r:/{filename}", mode="wb") as fw:
                data = base64.urlsafe_b64decode(buf)
                fw.write(data)
            stats = stat(f"r:/{filename}")
            if stats.st_size != size:
                print("File size mismatch!")
        # print(data.decode("ascii"))
        # print("*" * 30)
        break

ggwave.free(instance)

stream.stop_stream()
stream.close()

p.terminate()
