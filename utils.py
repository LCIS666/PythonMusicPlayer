import re

def parse_lyrics(lrc_content):
    lyrics = []
    lines = lrc_content.split('\n')
    for line in lines:
        match = re.match(r'\[(\d{2}:\d{2}\.\d{2})\](.*)', line)
        if match:
            time_str, text = match.groups()
            try:
                minutes, seconds = map(float, time_str.split(':'))
                time_seconds = minutes * 60 + seconds
                lyrics.append((time_seconds, text))
            except ValueError:
                continue
    lyrics.sort(key=lambda x: x[0])
    return lyrics

def format_time(time_in_seconds):
    minutes, seconds = divmod(int(time_in_seconds), 60)
    return f"{minutes:02}:{seconds:02}" 