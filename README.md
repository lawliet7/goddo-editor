  # goddo-editor
  Goddo Serenade's Video Editor  (** WIP **)
  
  <h5>Supported Video Formats:</h5>
  *.avi, *.mp4, *.wmv, *.webm, *.mov, *.flv, *.mkv
  
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
  
  | window |  key | description  |
  | --- | ------------ | ------------ |
  | all | esc  | quit  |
  | all | ctrl + s  | save  |
  | all | F2  | show all windows  |
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
  <b>ClickSlider</b> class modified based on answer from this post:
  <p style="text-align: center;"><span style="font-weight: 400;">“</span><a href="https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position/52690011#52690011" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">ClickSlider Stackoverflow Link</span></a><span style="font-weight: 400;">”, by </span><a href="https://www.flickr.com/photos/sebilden/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">David J</span></a><span style="font-weight: 400;">, licensed under </span><a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">CC BY 2.0</span></a></p>
  <b>FlowLayout</b> class based on answer from this post: [stackoverlow link](https://stackoverflow.com/q/46681266)
  <p style="text-align: center;"><span style="font-weight: 400;">“</span><a href="https://stackoverflow.com/q/46681266" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">FlowLayout Stackoverflow Link</span></a><span style="font-weight: 400;">”, by </span><a href="https://www.flickr.com/photos/sebilden/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">David J</span></a><span style="font-weight: 400;">, licensed under </span><a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener noreferrer"><span style="font-weight: 400;">CC BY 2.0</span></a></p>
  <p style="font-size: 0.9rem;font-style: italic;"><a href="https://www.flickr.com/photos/26726910@N03/13330784194">"Yoona (SNSD)"</a><span> by <a href="https://www.flickr.com/photos/26726910@N03">vikhoa</a></span> is licensed under <a href="undefined?ref=openverse&atype=html" style="margin-right: 5px;"></a><a href="undefined?ref=openverse&atype=html" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;"><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc_icon.svg?image_id=c54ab2a2-82b1-4cdf-9aef-fe298840d095" /><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc-by_icon.svg" /><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc-nc_icon.svg" /><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc-nd_icon.svg" /></a></p>
  <p style="font-size: 0.9rem;font-style: italic;"><a href="https://commons.wikimedia.org/w/index.php?curid=76503960">"File:Seohyun at Incheon International Airport in February 2019 (3).jpg"</a><span> by <a href="https://sparkles805.tistory.com">SparkleS805</a></span> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/2.0/?ref=openverse&atype=html" style="margin-right: 5px;">CC BY-NC-SA 2.0</a><a href="https://creativecommons.org/licenses/by-nc-sa/2.0/?ref=openverse&atype=html" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;"><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc_icon.svg?image_id=e1c5d8d8-e14f-439e-908b-39b9b5f8eea8" /><img style="height: inherit;margin-right: 3px;display: inline-block;" src="https://search.creativecommons.org/static/img/cc-by_icon.svg" /></a></p>
