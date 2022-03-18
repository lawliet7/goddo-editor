  # goddo-editor
  Goddo Serenade's Video Editor  (** WIP **)
  
  <h5>Supported Video Formats:</h5>
  *.mp4, *.wmv, *.mkv, *.webm, *.avi, *.mov, *.ts, *.m2ts', *.flv, *.asf

  <h6>Unsupported Video Formats:</h6>
  none found so far
  
  <h5>Environment - Use Conda</h5>
  - python 3.8
  - conda install -c conda-forge pyqt
  - conda install -c conda-forge opencv
  - conda install -c conda-forge imutils
  - conda install -c anaconda pyaudio
  - conda install -c conda-forge tinydb

  <h6>Testing only</h6>
  - conda install -c conda-forge pytest-qt
  - conda install -c conda-forge pytest-order
  - conda install -c conda-forge pyautogui
  - conda install -c conda-forge testfixtures

  <h6>Below are my package versions:</h6>

  | package |  version |
  | --- | ------------ |
  | pyqt | 5.9.2  |
  | opencv | 4.0.1  |
  | imutils | 0.5.4  |
  | pyaudio | 0.2.11  |
  | tinydb | 4.5.2  |
  | pytest-qt | 4.0.2  |
  | pytest-order | 1.0.1  |
  | pyautogui | 0.9.53  |
  | testfixtures | 6.18.3  |

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

  <h5>IDE setup:</h5>
  If you are using pycharm, you can directly create run configs and use working directory as root folder.  No big deal.  <br/>
  But if you are not then you would need to manually set the PYTHONPATH.  <br/>
  Below is example for vscode: <br/>

  ```javascript
  "terminal.integrated.env.windows": {
      "PYTHONPATH": "${workspaceFolder}"
  },
  "python.analysis.extraPaths": ["${workspaceFolder}"]
  ```
  - terminal.integrated.env.windows for running
  - python.analysis.extraPaths for autocomplete

  
  <h5>Run like this:</h5>
  python main.py
  
  <h4>shortcuts:</h4>
  
  | window |  key | description  |
  | --- | ------------ | ------------ |
  | all | esc  | quit  |
  | all | ctrl + s  | save  |
  | all | F2  | show all windows  |
  | file window | ctrl + w  | close file and reset gui  |
  | preview | space  | play/pause  |
  | preview | i  | mark in  |
  | preview | o  | mark out  |
  | preview | shift + i  | unmark in  |
  | preview | shift + o  | unmark out  |
  | preview | numpad +  | increase mouse wheel skip  |
  | preview | numpad -  | decrease mouse wheel skip  |
  | preview | [  |  go to in |
  | preview | ]  |  go to out |
  | preview | s  | switch between normal speed and max speed  |
  | preview (slider) | mouse wheel down  |  advance 1 min |
  | preview (slider) | mouse wheel up  |  go back 1 min |
  | preview | ->  |  advance 1 frame |
  | preview | <-  |  go back 5 frames |
  | preview output | f  |  switch between being restricting play to be within clip in/out range or not |
  | timeline | ctrl + p  | process output  |
  | timeline | ctrl + c  | copy clip |
  | timeline | ctrl + x  | cut clip |
  | timeline | ctrl + v  | paste clip |
  
  <h3>File List Help</h3>
  - to add tags, double click tag area (box under the name of the file)

  <h3>Timeline Help</h3>
  - once clips are in the timeline, in order to update them:
    1. first double click the clip to open in output window
    2. the seek bar will be linked to the clip and extra 30secs before/after to adjust
    3. whenever we change the in / out, it will immediately affect the clip on the timeline

  <h3>Credits:</h3>
  <p style="text-align: center;"><span style="font-weight: 400;"><strong>ClickSlider</strong> class modified based on answer from this </span><a href="https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position/52690011#52690011" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">Stackoverflow post</span></a><span style="font-weight: 400;">, by </span><a href="https://stackoverflow.com/users/6622587/eyllanesc" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">eyllanesc</span></a><span style="font-weight: 400;">, licensed under </span><a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">CC BY 4.0</span></a></p>
  <p style="text-align: center;"><span style="font-weight: 400;"><b>FlowLayout</b> class based on answer from this </span><a href="https://stackoverflow.com/questions/46681266/qscrollarea-with-flowlayout-widgets-not-resizing-properly/46727466#46727466" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">Stackoverflow post</span></a><span style="font-weight: 400;">, by </span><a href="https://stackoverflow.com/users/3564517/stefan-scherfke" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">Stefan Scherfke</span></a><span style="font-weight: 400;">, licensed under </span><a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">CC BY 3.0</span></a></p>
  <p style="text-align: center;"><span style="font-weight: 400;">Test videos are converted from this Youtube video </span><a href="https://www.youtube.com/watch?v=PcAGFgycZ3s" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">SNSD Girls Generation - Mr. Taxi - Live Mix</span></a><span style="font-weight: 400;">, by </span><a href="https://www.youtube.com/channel/UC5IWFlw9Idtd0F_mS2cJ8kw" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">Vadim Anokhin</span></a><span style="font-weight: 400;">, licensed under </span><a href="https://www.youtube.com/t/creative_commons" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">Creative Commons</span></a></p>
  