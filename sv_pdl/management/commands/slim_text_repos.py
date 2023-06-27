from pathlib import Path
from shutil import rmtree

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    @staticmethod
    def get_data_directories():
        root_data_path = Path(settings.CTS_LOCAL_DATA_PATH)
        data_dirs = []
        for path in root_data_path.iterdir():
            if path.suffix == ".json":
                continue
            elif path.is_dir():
                data_dirs.append(path)
                continue
            path.unlink()
        return data_dirs

    @staticmethod
    def remove_path_or_dirpath(path: Path):
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()

    def handle(self, *args, **options):
        data_dirs = self.get_data_directories()
        for data_dir in data_dirs:
            for path in data_dir.iterdir():
                if path.name in [".scaife-viewer.json", "data", ".scaife-viewer.yml"]:
                    continue
                self.remove_path_or_dirpath(path)
