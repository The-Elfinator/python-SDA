import pyarrow as pa
import pyarrow.parquet as pq

ValueType = int | list[int] | str | dict[str, str]


class Column:
    def __init__(self, name: str, value: ValueType, rows: int) -> None:
        self.__name: str = name
        self.__type: pa.DataType = self.__get_pa_type(value)
        self.__values: list[ValueType | None] = [None] * rows + [value]
        self.__nullable: bool = rows > 0

    @staticmethod
    def __get_pa_type(value: ValueType) -> pa.DataType:
        if isinstance(value, list):
            return pa.list_(pa.int64())
        elif isinstance(value, int):
            return pa.int64()
        elif isinstance(value, str):
            return pa.string()
        elif isinstance(value, dict):
            return pa.map_(pa.string(), pa.string())
        else:
            raise ValueError(f"Found unknown type: {type(value)}")

    def update(self, value: ValueType | None) -> None:
        if value is None:
            self.__nullable = True
        elif self.__type != self.__get_pa_type(value):
            raise TypeError(f"Field {self.get_name()} has different types")
        self.__values.append(value)

    def get_name(self) -> str:
        return self.__name

    def get_type(self) -> pa.DataType:
        return self.__type

    def get_values(self) -> list[ValueType | None]:
        return self.__values

    def get_nullable(self) -> bool:
        return self.__nullable


def save_rows_to_parquet(rows: list[dict[str, ValueType]], output_filepath: str) -> None:
    """
    Save rows to parquet file.

    :param rows: list of rows containing data.
    :param output_filepath: local filepath for the resulting parquet file.
    :return: None.
    """
    columns: dict[str, Column] = {}
    rows_cnt = 0
    for row in rows:
        cur_col = set(columns.keys())
        for key, value in row.items():
            column_value = columns.get(key)
            if column_value is None:
                columns[key] = Column(key, value, rows_cnt)
            else:
                columns[key].update(value)
                cur_col.remove(key)
        for key in cur_col:
            columns[key].update(None)
        rows_cnt += 1
    scheme = pa.schema([pa.field(c.get_name(), c.get_type(), c.get_nullable())
                        for c in columns.values()])
    table = pa.Table.from_arrays(
        [pa.array(c.get_values(), type=c.get_type()) for c in columns.values()], schema=scheme
    )
    pq.write_table(table, output_filepath)
