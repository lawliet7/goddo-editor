# goddo-editor
Goddo Serenade's Video Editor

Supported Video Formats:
*.avi, *.mp4, *.wmv, *.webm, *.mov, *.flv, *.mkv

Environment - Use Conda
- python 3.8
- conda install pyqt
- conda install -c conda-forge opencv
- conda install -c conda-forge imutils
- conda install -c anaconda pyaudio

**use conda as installing pyaudio is otherwise very painful, disadvantage is obviously we can't use pyqt6

**NOTE: conda forge unfortunately don't have pyqt6 so we are stuck with pyqt 5 for now

**NOTE: to play audio, player will create temp file in same directory called audio.wav.
Because of this start will be very slow if we are processing big video files.

Environment Variables:
- LOG LEVEL (optional) = levels in logging pkg
    - CRITICAL
    - ERROR
    - WARNING
    - INFO
    - DEBUG

* if you have icon put it in main package as icon.png

Run like this:

python main.py {VIDEO} {INITIAL_OFFSET - OPTIONAL}

shortcuts:
- spacebar to pause/play
- i to mark in
- o to mark out
- left/right to move 1 frame