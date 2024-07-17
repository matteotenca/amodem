import argparse
import base64
import pprint
import signal
import sys
import time
import os
from pathlib import Path

import ggwave
import pyaudio

p = None
stream = None


def handler(signum, frame):
    global p, stream
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()
    exit(0)


signal.signal(signal.SIGINT, handler)
# parser = argparse.ArgumentParser(add_help=False)
# parser.add_argument("-t", "--type", choices=[0, 1, 2])
# parser.add_argument(
#     '-l', '--list-devices', action='store_true',
#     help='show list of audio devices and exit')
# if args.list_devices:
#     print(sd.query_devices())
#     parser.exit(0)
# parser = argparse.ArgumentParser(
#     description=__doc__,
#     formatter_class=argparse.RawDescriptionHelpFormatter,
#     parents=[parser])
# # parser.add_argument(
# #     'filename', metavar='FILENAME',
# #     help='audio file to be played back')
# parser.add_argument(
#     '-d', '--device', type=int_or_str,
#     help='output device (numeric ID or substring)')
# parser.add_argument(
#     '-b', '--blocksize', type=int, default=2048,
#     help='block size (default: %(default)s)')
# parser.add_argument(
#     '-q', '--buffersize', type=int, default=200,
#     help='number of blocks used for buffering (default: %(default)s)')
# parser.add_argument(
#     '-r', '--samplerate', type=int, help='sampling rate')
# args = parser.parse_args(remaining)

p = pyaudio.PyAudio()
#
# host_api_info = p.get_default_host_api_info()
# pprint.pprint(host_api_info)
# print("*")
# input_device_info = p.get_default_input_device_info()
# pprint.pprint(input_device_info)
# print("*")
# output_device_info = p.get_default_output_device_info()
# pprint.pprint(output_device_info)
# print("*")
# device_count = p.get_device_count()
# pprint.pprint(device_count)
# print("*")
# device_info = p.get_device_info_by_index(5)
# pprint.pprint(device_info)
# print("**")
# host_api_count = p.get_host_api_count()
# pprint.pprint(host_api_count)
# for i in range(host_api_count):
#     info = p.get_host_api_info_by_index(i)
#     pprint.pprint(info)
#     print("*")
# p.terminate()
# exit(0)
# generate audio waveform for string "hello python"
# bbbb = "ZXhjbHVkZSA9IFsKICAgICIuYnpyIiwKICAgICIuZGlyZW52IiwKICAgICIuZWdncyIsCiAgICAiLmdpdCIsCiAgICAiLmdpdC1yZXdyaXRlIiwKICAgICIuaGciLAogICAgIi5pcHluYl9jaGVja3BvaW50cyIsCiAgICAiLm15cHlfY2FjaGUiLAogICAgIi5ub3giLAogICAgIi5wYW50cy5kIiwKICAgICIucHllbnYiLAogICAgIi5weXRlc3RfY2FjaGUiLAogICAgIi5weXR5cGUiLAogICAgIi5ydWZmX2NhY2hlIiwKICAgICIuc3ZuIiwKICAgICIudG94IiwKICAgICIudmVudiIsCiAgICAiLnZzY29kZSIsCiAgICAiX19weXBhY2thZ2VzX18iLAogICAgIl9idWlsZCIsCiAgICAiYnVjay1vdXQiLAogICAgImJ1aWxkIiwKICAgICJkaXN0IiwKICAgICJub2RlX21vZHVsZXMiLAogICAgInNpdGUtcGFja2FnZXMiLAogICAgInZlbnYiLAogICAgIm9sZCIsCiAgICAic2NyaXB0cyIsCl0KCnRhcmdldC12ZXJzaW9uID0gInB5MzEwIgoK"
# print(base64.urlsafe_b64decode(bbbb).decode("ascii"))
# exit(0)
# pprint.pprint(ggwave.getDefaultParameters())

protocol = 8
encode = "yes"
if len(sys.argv) > 1:
    file = sys.argv[1]
else:
    print("Please specify only the file name to read")
    exit(1)
if not Path(file).is_file():
    print("File {file} is not a file/does not exists")
    exit(1)

if len(sys.argv) > 2:
    protocol = int(sys.argv[2])
if len(sys.argv) > 3:
    encode = sys.argv[3]

# file = "tox.ini"
# 0 = Normal
# 1 = Fast
# 2 = Fastest
# 3 = [U] Normal
# 4 = [U] Fast
# 5 = [U] Fastest
# 6 = [DT] Normal
# 7 = [DT] Fast
# 8 = [DT] Fastest
s = os.stat(file)
size = s.st_size
name = Path(file).name
if encode == "yes":
    with open(file, "rb") as f:
        # with open("LICENSE.bin", "wb") as fw:
        base = base64.urlsafe_b64encode(f.read()).decode("ascii")
        # base64.encode(f, fw)
else:
    with open(file, "r") as f:
        base = f.read()

ar = [base[i:i+140] for i in range(0, len(base), 140)]
ln = len(ar)
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True,
                frames_per_buffer=4096)
if encode == "yes":
    header = '{0}"pieces": {1}, "filename": "{2}", "size": {3}{4}'.format(
        "{", str(ln), name, str(size), "}"
    )
    print("Sending header, length:", len(header))
    waveform = ggwave.encode(header, protocolId=protocol, volume=60)
    stream.write(waveform, len(waveform) // 4)
# signal.raise_signal(signal.SIGINT)
waveform = ggwave.encode("VOX", protocolId=protocol, volume=60)
stream.write(waveform, len(waveform) // 4)
print("Sending data, length):", len(base))
q = 1
t = time.time()
for piece in ar:
    print(f"Piece {q}/{ln} {q*140} B", end="\r", flush=True)
    waveform = ggwave.encode(piece, protocolId=protocol, volume=60)
    stream.write(waveform, len(waveform) // 4)
    q += 1
tt = time.time() - t
print()
stream.stop_stream()
stream.close()
print("Time taken to encode waveform:", tt)
print("Speed:", len(base) / tt, "B/s")
# pprint.pprint(p.get_default_host_api_info())
p.terminate()
# exit(0)
# print("Transmitting text 'hello python' ...")
#     stream.stop_stream()
#     stream.close()
#     tt = time.time() - t
#     print("Time taken to encode waveform:", tt)
#     print("Speed:", size / tt, "B/s")
# else:
#     print("error")
#
# p.terminate()
