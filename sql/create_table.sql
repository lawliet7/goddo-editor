CREATE TABLE IF NOT EXISTS video (
	video_id INTEGER PRIMARY KEY,
	video_path TEXT NOT NULL,
  	alias TEXT
);

CREATE TABLE IF NOT EXISTS tag (
    tag_id INTEGER PRIMARY KEY,
	tag_key TEXT NOT NULL,
	tag_value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS state (
    state_id INTEGER PRIMARY KEY,
	video_id INTEGER NOT NULL,
	in_frame INTEGER,
  	out_frame INTEGER,
	pos INTEGER NOT NULL,
	volume NUMERIC NOT NULL,
	FOREIGN KEY(video_id) REFERENCES video(video_id)
);

CREATE TABLE IF NOT EXISTS clip (
    clip_id INTEGER PRIMARY KEY,
	video_id INTEGER NOT NULL,
	type TEXT NOT NULL,
	in_frame INTEGER,
  	out_frame INTEGER,
	FOREIGN KEY(video_id) REFERENCES video(video_id)
);

CREATE TABLE IF NOT EXISTS timeline_window (
    timeline_id INTEGER PRIMARY KEY,
	pos INTEGER NOT NULL,
	scroll_bar_pos INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS timeline_clip (
    timeline_id INTEGER,
	clip_id INTEGER,
	start_pos INTEGER NOT NULL,
	PRIMARY KEY(timeline_id,clip_id),
	FOREIGN KEY(timeline_id) REFERENCES timeline_window(timeline_id),
	FOREIGN KEY(clip_id) REFERENCES clip(clip_id)
);

CREATE TABLE IF NOT EXISTS clip_tag (
    tag_id INTEGER,
	clip_id INTEGER,
	PRIMARY KEY(tag_id,clip_id),
	FOREIGN KEY(tag_id) REFERENCES tag(tag_id),
	FOREIGN KEY(clip_id) REFERENCES clip(clip_id)
);

CREATE TABLE IF NOT EXISTS video_tag (
    tag_id INTEGER,
	video_id INTEGER,
	PRIMARY KEY(tag_id,video_id),
	FOREIGN KEY(tag_id) REFERENCES tag(tag_id),
	FOREIGN KEY(video_id) REFERENCES video(video_id)
);
