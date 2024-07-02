import pandas as pd
import numpy as np
import os
import sys
import re

from typing import TypedDict, List, Callable, Any, Dict


class Dataset:
    def __init__(self, filepath: str, lines: List[str]):
        self.filepath = filepath
        self.filename = filepath.split("/")[-1]
        self.raw_lines: List[str] = lines

        self.schema: Dict[int, str] = {}
        self.data: Dict[str, List[Any]] = {}

        self.df: pd.DataFrame = pd.DataFrame()

    def make_schema(self):
        header = self.raw_lines[0]

        parts = header.split('"')
        parts = [re.sub(r"\s+", " ", field) for field in parts]
        parts = [part for part in parts if part != " " and part != ""]
        for ix, row_name in enumerate(parts):
            self.schema[row_name] = ix
            self.data[row_name] = []

    def with_df(self):
        self.df = pd.DataFrame(self.data)

    def gather(self):
        self.make_schema()

        for line in self.raw_lines[1:]:
            columns = re.split(r"\s+", line)
            for k, ix in self.schema.items():
                if ix >= len(columns):
                    self.data[k].append(None)
                    continue

                v = columns[ix]
                self.data[k].append(v)

        self.with_df()
        return self

    def get(self, column_name: str, ix: int):
        data = self.data.get(column_name)

        if not data or len(data) <= ix:
            return None

        return data[ix]

    def column_transform(self, key: str, transform: Callable):
        if not self.data.get(key):
            return

        for ix in range(len(self.data[key])):
            self.data[key][ix] = transform(self.data[key][ix])

        self.with_df()

    def column_rename(self, key: str, new_key: str):
        self.data[new_key] = self.data[key]
        del self.data[key]
        self.with_df()

    def squeeze(self, *keys: str):
        klist = [*self.data.keys()]
        for k in klist:
            if k not in keys:
                del self.data[k]

        self.with_df()

    def extend(self, column_name: str, transform: Callable[[int, Any], Any]):
        self.data[column_name] = []

        for ix in range(self.df.shape[0]):
            ncv = transform(ix, self)
            self.data[column_name].append(ncv)

        self.with_df()

    def merge(self, other):
        for k in self.data.keys():
            self.data[k].extend(other.data[k])

        self.with_df()


class ETL:
    def __init__(self):
        self.datasets: List[Dataset] = []

    def load(self, filepath: str):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            ds = Dataset(filepath=filepath, lines=f.readlines()[2:])
            ds.gather()
            self.datasets.append(ds)

        return self

    def load_dir(self, folder: str, ext: str):
        files = os.listdir(folder)
        [self.load(f"{folder}/{file}") for file in files if file.endswith(ext)]

        print(f"{len(self.datasets)} datasets loaded from {folder}/*{ext}")

        return self

    def map_all(self, fn: Callable[[Dataset], Any]):
        [fn(ds) for ds in self.datasets]

    def column_transform_all(self, key: str, transform: Callable):
        for ds in self.datasets:
            ds.column_transform(key, transform)

    def squeeze_all(self, *keys: str):
        for ds in self.datasets:
            ds.squeeze(*keys)

    def column_rename_all(self, key: str, new_key: str):
        for ds in self.datasets:
            ds.column_rename(key, new_key)

    def extend_all(
        self, column_name: str, transform: Callable[[int, pd.DataFrame], Any]
    ):
        for ds in self.datasets:
            ds.extend(column_name=column_name, transform=transform)

    def crush(self, reducers: Dict[str, Callable[[Dataset], bool]]):
        crush_groups: Dict[str, List[Dataset]] = {k: [] for k in reducers.keys()}

        for ds in self.datasets:
            for group, reducer in reducers.items():
                if reducer(ds):
                    crush_groups[group].append(ds)

        crushed: List[Dataset] = []

        for cg in crush_groups.values():
            if len(cg) == 0:
                continue

            parent = cg[0]

            [parent.merge(other_dataset) for other_dataset in cg[1:]]

            crushed.append(parent)

        self.datasets = crushed
