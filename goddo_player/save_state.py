from typing import List

import cv2
from tinydb import TinyDB, Query
from dataclasses import dataclass
import pathlib

from goddo_player.DragAndDrop import VideoClipDragItem


@dataclass
class State:
    save_file: str
    video_file: str

    def __post_init__(self):
        is_existing_file = pathlib.Path(self.save_file).resolve().exists()

        self.db = TinyDB(self.save_file)
        self.video_table = self.db.table('video')
        self.timeline_table = self.db.table('timeline')
        self.preview_window_table = self.db.table('preview_window')

        abs_path_str = str(pathlib.Path(self.video_file).resolve())

        cap = cv2.VideoCapture(self.video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)

        if is_existing_file:
            id = self.video_table.upsert({'video_path': abs_path_str, 'alias': None, 'fps': fps},
                                         Query().video_path == abs_path_str)
            self.cur_video = self.video_table.get(Query().video_path == abs_path_str)
            self.videos = self.video_table.all()

            # self.videos

            # todo: handle different video
            preview_window_state = self.preview_window_table.get(Query().tab == 'source')
            if preview_window_state:
                self.source = preview_window_state['source']

            timeline = self.timeline_table.get(Query().name == 'default') or {'name': 'default', 'clips': []}
            self.timeline = Timeline(timeline['name'],
                                     [VideoClipDragItem(**x, video=self.cur_video) for x in timeline['clips']])
        else:
            self.video_table.insert({'video_path': abs_path_str, 'alias': None, 'fps': fps})
            self.cur_video = self.video_table.get(Query().video_path == abs_path_str)
            self.videos = [self.cur_video]
            self.source = {'video_id': self.cur_video.doc_id, 'position': 0, 'in_frame': None, 'out_frame': None,
                           'volume': 1, 'is_muted': False}
            self.timeline = Timeline('default', [])

        print(self.videos)
        print(self.source)
        print(self.timeline)
        # self.db_conn = sqlite3.connect(self.save_file)
        # self.cursor = self.db_conn.cursor()
        #
        # with open("sql/create_table.sql") as sql_file:
        #     sql_as_string = sql_file.read()
        #     self.cursor.executescript(sql_as_string)
        #
        # data = self.cursor.execute("SELECT * FROM video WHERE video_path = ?", [self.save_file])
        # print(f'data: {data}')

        # for row in self.cursor.execute('SELECT * FROM video'):
        #     print(row)

    def save(self, main_window):
        print(self.videos)
        print(self.source)
        print(self.timeline)
        # video_id = self.video_table.upsert({'video_path': str(abs_path), 'alias': None}, Query().video_path == str(abs_path))[0]
        self.preview_window_table.upsert({'tab': 'source', 'source': self.source }, Query().tab.one_of(['source', 'timeline']))
        # print(self.timeline['clips'][0].__dict__)
        clips = [x.__dict__ for x in self.timeline.clips]
        self.timeline_table.upsert({'name': 'default', 'clips': clips}, Query().name == self.timeline.name)

        # pass
        # self.db_conn.execute("")


@dataclass
class Timeline:
    name: str
    clips: List[VideoClipDragItem]
