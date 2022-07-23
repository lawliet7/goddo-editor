import time
import numpy as np
import av
import pyaudio

# container = av.open(r'C:\Users\William\dev\vid\bda018.mp4')
container = av.open(r'C:\Users\William\dev\bonds.mp4')
# container.seek(10000)
print(container)
print(container.bit_rate)

# for frame in container.decode(video=0):
#     frame.to_image().save('frame-%04d.jpg' % frame.index)

g = container.decode(audio=0)
frame = next(g)
format = frame.format
print(format.bits)
print(format.bytes)
print(frame.rate)
print(frame.samples)

pa = pyaudio.PyAudio()
audio_stream = pa.open(format=pyaudio.paInt32,channels=2,rate=44100,output=True)

# i = 0
# for _ in g:
#     i = i + 1
#     if i % 1000 == 0:
#         print(i)
# print(i)

frames = [next(g).to_ndarray() for _ in range(1000)]
audio_stream.write(np.concatenate(frames))
time.sleep(2)


# print(frame.to_ndarray())
# https://pyav.org/docs/stable/api/container.html#input-containers
# conda install av -c conda-forge

