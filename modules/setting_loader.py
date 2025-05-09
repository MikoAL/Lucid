import json
from pathlib import Path

settings_path = Path(Path(__file__).resolve().parent.parent/"settings")

def load_settings(settings_folder_path=settings_path):
    with open(settings_path/"settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    all_settings = {}
    for key, item in settings.items():
        file_path = settings_path/f"{key}"/f"{settings[key]}.json"
        with open(file_path) as file:
            all_settings.update({key: json.load(file)})
    return all_settings

if "__main__" == __name__:
    print(load_settings())