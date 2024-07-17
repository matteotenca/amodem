import sys

import ggwave
import sounddevice as sd
import soundfile as sf

class Recorder:
    def __init__(self):
        self.bufsize = 4096

        self.audio_stream = sd.RawInputStream(
            samplerate=44100,
            blocksize=self.bufsize,
            channels=1, dtype='int16')
        self.audio_stream.start()

    def read(self, size):
        data, overflowed = self.audio_stream.read(size)
        if overflowed:
            raise OverflowError("Overflow reading from audio device")
        return data

    def close(self):
        self.audio_stream.stop()
        self.audio_stream.close()


class Player:
    def __init__(self):
        self.buffer_length_ms = 10
        self.buffer_size = int(44100 * (self.buffer_length_ms / 1000))

        self.audio_stream = sd.RawOutputStream(
            samplerate=44100,
            blocksize=self.buffer_size,
            channels=1, dtype='int16')

        self.audio_stream.start()

    def write(self, data):
        self.audio_stream.write(data)

    def close(self):
        self.audio_stream.stop()
        self.audio_stream.close()


if sys.argv[1] == 'play':
    p = Player()
    # generate audio waveform for string "hello python"
    waveform = ggwave.encode("hello python", protocolId=0, volume=15)
    print("Transmitting text 'hello python' ...")
    p.write(waveform)
    p.close()
    # with open(r"r:\out.raw", "wb") as f:
    #     f.write(waveform)
    with sf.SoundFile(r"r:\fc8.wav", mode='w', samplerate=44100,
                      channels=1) as file:
        file.buffer_write(waveform, "int16")
        # pass

else:
    try:
        r = Recorder()
        print('Listening ... Press Ctrl+C to stop')
        instance = ggwave.init()
        while True:
            d = r.read(1024)
            res = ggwave.decode(instance, d)
            if res is not None:
                try:
                    print('Received text: ' + res.decode("utf-8"))
                except BaseException as e:
                    raise e
    except KeyboardInterrupt:
        pass
    finally:
        r.close()
        ggwave.free(instance)



#
#
# print('Listening ... Press Ctrl+C to stop')
# instance = ggwave.init()
#
#
#
# try:
#     while True:
#         data = Recorder.read(1024)
#         res = ggwave.decode(instance, data)
#         if res is not None:
#             try:
#                 print('Received text: ' + res.decode("utf-8"))
#             except:
#                 pass
# except KeyboardInterrupt:
#     pass
#
# ggwave.free(instance)
#
# stream.stop_stream()
# stream.close()
#
# p.terminate()
