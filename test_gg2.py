#!/usr/bin/env python3
"""Create a recording with arbitrary duration.

The soundfile module (https://python-soundfile.readthedocs.io/)
has to be installed!

"""
import argparse

# import tempfile
import queue
import sys
import threading

import ggwave
import sounddevice as sd
import soundfile as sf


# import numpy  # Make sure NumPy is loaded before it is used in the callback

# assert numpy  # avoid "imported but unused" message (W0611)


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
# parser.add_argument(
#     'filename', metavar='FILENAME',
#     help='audio file to be played back')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-b', '--blocksize', type=int, default=2048,
    help='block size (default: %(default)s)')
parser.add_argument(
    '-q', '--buffersize', type=int, default=200,
    help='number of blocks used for buffering (default: %(default)s)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)
if args.blocksize == 0:
    parser.error('blocksize must not be zero')
if args.buffersize < 1:
    parser.error('buffersize must be at least 1')

q = queue.Queue(maxsize=0)
event = threading.Event()

ggwave.disableLog()
params = ggwave.getDefaultParameters()
params["samplerate"] = 44100
params["sampleFormatInp"] = 44100
params["sampleFormatOut"] = 44100
params["operatingMode"] = 6
instance = ggwave.init(params)

global ooo
ooo = 0


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status.input_overflow:
        # print('Input overflow: increase blocksize?', file=sys.stderr, flush=True)
        ooo += 1
    #     raise sd.CallbackAbort
    assert not status
    # try:
    #     q.put(indata)
    # except queue.Empty as e:
    #     print('Buffer is empty: increase buffersize?', file=sys.stderr)
    #     raise sd.CallbackAbort from e
    # if len(data) < len(outdata):
    #     outdata[:len(data)] = data
    #     outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
    #     raise sd.CallbackStop
    # else:
    #     outdata[:] = data
    # if status:
    #     print(status, file=sys.stderr)
    # q.put(indata.copy())
    q.put(indata)


i = 0
try:
    if args.samplerate is None:
        # device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        # args.samplerate = device_info['default_samplerate']
        # if args.filename is None:
        #     args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
        #                                     suffix='.wav', dir='')

        # Make sure the file is opened before recording anything:
        # with sf.SoundFile(args.filename, mode='x', samplerate=args.samplerate,
        #                   channels=args.channels, subtype=args.subtype) as file:
        # with open(r"r:\test.bin", "wb") as f:
        # with open(r"r:\out.raw", "rb") as f:
        #     buf = f.read(1000000000)
        #     res = ggwave.decode(instance, buf)
        #     if res is not None:
        #         try:
        #             print('Received text: ' + res.decode("utf-8"))
        #         except BaseException as e:
        #             raise e

        filein = sf.SoundFile(r"r:\gg2.wav", mode='r')
        while True:
            bb = filein.buffer_read(dtype="int16")
            if not bb:
                break
            re = ggwave.decode(instance, bytes(bb))
            if re is not None:
                try:
                    print("###")
                    print('Received text: ' + re.decode("utf-8"))
                    break
                except BaseException as e:
                    raise e
        filein.close()

        file = sf.SoundFile(r"r:\gg2.wav", mode='w', samplerate=44100,
                            channels=1)

        with sd.RawInputStream(samplerate=44100, dtype='int16', blocksize=4096,
                               channels=1, callback=callback, finished_callback=event.set) as input_stream:
            input_stream.start()
            print('#' * 80)
            print('press Ctrl+C to stop the recording')
            print('#' * 80)
            while True:
                # file.write(q.get())
                dt = q.get()
                buf = bytes(dt)
                if buf is not None:
                    res = ggwave.decode(instance, buf)
                    file.buffer_write(buf, "int16")
                    # i += 1
                    # print(f"{i} {len(buf)}       ", end="\r", flush=True)
                    if res is not None:
                        try:
                            print("********************")
                            print('Received text: ' + res.decode("utf-8"))
                        except BaseException as e:
                            raise e
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except queue.Full:
    # A timeout occurred, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
finally:
    input_stream.stop()
    input_stream.close()
    ggwave.free(instance)
    file.close()
    print(ooo)
