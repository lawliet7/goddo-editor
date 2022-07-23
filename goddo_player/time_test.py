

# =TEXT(FLOOR(B837/60/60),"00")&":"&TEXT(MOD(FLOOR(B837/60),60),"00")&":"&TEXT(MOD(FLOOR(B837),60),"00")&"."&TEXT(FLOOR(mod(A837,$B$1)),"00")

from math import floor


prev_frame = 0
fps = 29.97
for i in range(1,334683):
    hours = floor(i / fps / 60 / 60)
    mins = floor(i / fps / 60) % 60
    secs = floor(i / fps) % 60
    frames = floor(i % fps)
    time_str = f'{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}'
    print(type(frames))

    # if prev_frame == 29:
    #     if frames != 0:
    #         print(time_str)
    #         prev_frame = 0
    #     else:
    #         prev_frame = frames
    # else:
    #     if prev_frame != frames-1:
    #         print(f'time {time_str} prev {prev_frame} cur {frames}')
    #     prev_frame = frames

    # if i % 1000 == 0:
    #     print(time_str)
    # if i == 30:
    #     break