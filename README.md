# goddo-editor
Goddo Serenade's Video Editor

Supported Video Formats:
*.avi, *.mp4, *.wmv, *.webm, *.mov, *.flv, *.mkv

Environment - Use Conda
- python 3.8
- conda install pyqt
- conda install -c conda-forge opencv
- conda install -c conda-forge imutils

**NOTE: conda forge unfortunately don't have pyqt6 so we are stuck with pyqt 5 for now

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