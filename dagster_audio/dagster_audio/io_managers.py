from dagster import IOManager, io_manager
import pandas as pd
import os

class FileSystemIOManager(IOManager):
    def __init__(self, base_dir: str):
        self._base_dir = base_dir

    def _get_path(self, context) -> str:
        return os.path.join(
            self._base_dir,
            context.asset_key.path[-1] + ".parquet"
        )

    def handle_output(self, context, obj):
        if isinstance(obj, pd.DataFrame):
            obj.to_parquet(self._get_path(context))
        else:
            raise Exception(f"Unsupported type for IO Manager: {type(obj)}")

    def load_input(self, context):
        path = self._get_path(context)
        if os.path.exists(path):
            return pd.read_parquet(path)
        return None

@io_manager
def filesystem_io_manager():
    return FileSystemIOManager("/opt/dagster/dagster_home/storage") 