# goddo-editor
Goddo Serenade's Video Editor  (** WIP **)

<h5>Supported Video Formats:</h5>
*.avi, *.mp4, *.wmv, *.webm, *.mov, *.flv, *.mkv

<h5>Environment - Use Conda</h5>
- python 3.8
- conda install pyqt
- conda install -c conda-forge opencv
- conda install -c conda-forge imutils
- conda install -c anaconda pyaudio
- conda install -c conda-forge tinydb

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

<h5>Run like this:</h5>
python main.py {VIDEO} {INITIAL_OFFSET - OPTIONAL}

<h4>shortcuts:</h4>
- spacebar: to pause/play
- i:  to mark in
- o: to mark out
- left/right: to move 1 frame
- s: to switch between normal and max speed

| window |  key | description  |
| --- | ------------ | ------------ |
| all | esc  | quit  |
| preview | space  | play/pause  |
| preview | i  | mark in  |
| preview | o  | mark out  |
| preview | shift + i  | unmark in  |
| preview | shift + o  | unmark out  |
| preview | [  |  go to in |
| preview | ]  |  go to out |
| preview | ->  |  advance 1 frame |
| preview | <-  |  go back 5 frames |
| preview | s  | switch between normal speed and max speed  |
| file | ctrl + s  | save  |

<h3>Credits:</h3>
<b>ClickSlider</b> class modified based on answer from this post:
https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position/52690011#52690011

<b>FlowLayout</b> class based on answer from this post:
https://stackoverflow.com/q/46681266
