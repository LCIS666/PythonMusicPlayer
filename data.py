import json
import os

class DataHandler:
    def __init__(self, data_file):
        self.data_file = data_file
        self.playlists = {"默认电台": []}
        self.current_playlist_name = "默认电台"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.playlists = data.get('playlists', {"默认电台": []})
                    self.current_playlist_name = data.get('current_playlist_name', "默认电台")
                    
                    if self.current_playlist_name not in self.playlists:
                        self.current_playlist_name = "默认电台"
                        if "默认电台" not in self.playlists:
                            self.playlists["默认电台"] = []
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载播放列表数据时出错: {e}")
                self.playlists = {"默认电台": []}
                self.current_playlist_name = "默认电台"
        else:
            self.save_data(self.playlists, self.current_playlist_name)

    def save_data(self, playlists, current_playlist_name):
        data = {
            'playlists': playlists,
            'current_playlist_name': current_playlist_name
        }
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"保存播放列表数据时出错: {e}") 