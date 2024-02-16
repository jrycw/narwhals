from __future__ import annotations
import polars_api_compat

from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import NoReturn

import numpy as np
import pandas as pd
from pandas.api.types import is_extension_array_dtype

from polars_api_compat.utils import validate_column_comparand

if TYPE_CHECKING:
    from dataframe_api import Column as ColumnT
    from dataframe_api.typing import DType
    from dataframe_api.typing import NullType
    from dataframe_api.typing import Scalar

    from polars_api_compat.pandas.dataframe_object import DataFrame
else:
    ColumnT = object


NUMPY_MAPPING = {
    "Int64": "int64",
    "Int32": "int32",
    "Int16": "int16",
    "Int8": "int8",
    "UInt64": "uint64",
    "UInt32": "uint32",
    "UInt16": "uint16",
    "UInt8": "uint8",
    "boolean": "bool",
    "Float64": "float64",
    "Float32": "float32",
}


class Series(ColumnT):
    def __init__(
        self,
        series: pd.Series[Any],
        *,
        api_version: str,
    ) -> None:
        """Parameters
        ----------
        df
            DataFrame this column originates from.
        """

        self._name = series.name
        assert self._name is not None
        self._series = series
        self._api_version = api_version

    def __repr__(self) -> str:  # pragma: no cover
        header = f" Standard Column (api_version={self._api_version}) "
        length = len(header)
        return (
            "┌"
            + "─" * length
            + "┐\n"
            + f"|{header}|\n"
            + "| Add `.column` to see native output         |\n"
            + "└"
            + "─" * length
            + "┘\n"
        )

    def __iter__(self) -> NoReturn:
        msg = ""
        raise NotImplementedError(msg)

    def _from_series(self, series: pd.Series) -> Series:
        return Series(
            series.rename(series.name, copy=False),
            api_version=self._api_version,
        )

    # In the standard
    def __column_namespace__(
        self,
    ) -> polars_api_compat.pandas.Namespace:
        return polars_api_compat.pandas.Namespace(
            api_version=self._api_version,
        )

    @property
    def name(self) -> str:
        return self._name  # type: ignore[no-any-return]

    @property
    def column(self) -> pd.Series[Any]:
        return self._series

    @property
    def dtype(self) -> DType:
        return polars_api_compat.pandas.map_pandas_dtype_to_standard_dtype(
            self._series.dtype,
        )

    @property
    def parent_dataframe(self) -> DataFrame | None:
        return self._df

    def take(self, indices: Series) -> Series:
        return self._from_series(
            self.column.iloc[validate_column_comparand(self, indices)]
        )

    def filter(self, mask: Series) -> Series:
        ser = self.column
        return self._from_series(ser.loc[validate_column_comparand(self, mask)])

    def get_value(self, row_number: int) -> Any:
        ser = self.column
        return ser.iloc[row_number]

    def slice_rows(
        self,
        start: int | None,
        stop: int | None,
        step: int | None,
    ) -> Series:
        return self._from_series(self.column.iloc[start:stop:step])

    # Binary comparisons

    def __eq__(self, other: Series | Any) -> Series:  # type: ignore[override]
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser == other).rename(ser.name, copy=False))

    def __ne__(self, other: Series | Any) -> Series:  # type: ignore[override]
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser != other).rename(ser.name, copy=False))

    def __ge__(self, other: Series | Any) -> Series:
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser >= other).rename(ser.name, copy=False))

    def __gt__(self, other: Series | Any) -> Series:
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser > other).rename(ser.name, copy=False))

    def __le__(self, other: Series | Any) -> Series:
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser <= other).rename(ser.name, copy=False))

    def __lt__(self, other: Series | Any) -> Series:
        other = validate_column_comparand(self, other)
        ser = self.column
        return self._from_series((ser < other).rename(ser.name, copy=False))

    def __and__(self, other: Series | bool | Scalar) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser & other).rename(ser.name, copy=False))

    def __rand__(self, other: Series | Any) -> Series:
        return self.__and__(other)

    def __or__(self, other: Series | bool | Scalar) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser | other).rename(ser.name, copy=False))

    def __ror__(self, other: Series | Any) -> Series:
        return self.__or__(other)

    def __add__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser + other).rename(ser.name, copy=False))

    def __radd__(self, other: Series | Any) -> Series:
        return self.__add__(other)

    def __sub__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser - other).rename(ser.name, copy=False))

    def __rsub__(self, other: Series | Any) -> Series:
        return -1 * self.__sub__(other)

    def __mul__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser * other).rename(ser.name, copy=False))

    def __rmul__(self, other: Series | Any) -> Series:
        return self.__mul__(other)

    def __truediv__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser / other).rename(ser.name, copy=False))

    def __rtruediv__(self, other: Series | Any) -> Series:
        raise NotImplementedError

    def __floordiv__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser // other).rename(ser.name, copy=False))

    def __rfloordiv__(self, other: Series | Any) -> Series:
        raise NotImplementedError

    def __pow__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser**other).rename(ser.name, copy=False))

    def __rpow__(self, other: Series | Any) -> Series:  # pragma: no cover
        raise NotImplementedError

    def __mod__(self, other: Series | Any) -> Series:
        ser = self.column
        other = validate_column_comparand(self, other)
        return self._from_series((ser % other).rename(ser.name, copy=False))

    def __rmod__(self, other: Series | Any) -> Series:  # pragma: no cover
        raise NotImplementedError

    def __divmod__(self, other: Series | Any) -> tuple[Series, Series]:
        quotient = self // other
        remainder = self - quotient * other
        return quotient, remainder

    # Unary

    def __invert__(self: Series) -> Series:
        ser = self.column
        return self._from_series(~ser)

    # Reductions

    def any(self, *, skip_nulls: bool | Scalar = True) -> Scalar:
        ser = self.column
        return ser.any()

    def all(self, *, skip_nulls: bool | Scalar = True) -> Scalar:
        ser = self.column
        return ser.all()

    def min(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.min()

    def max(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.max()

    def sum(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.sum()

    def prod(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.prod()

    def median(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.median()

    def mean(self, *, skip_nulls: bool | Scalar = True) -> Any:
        ser = self.column
        return ser.mean()

    def std(
        self,
        *,
        correction: float | Scalar | NullType = 1.0,
        skip_nulls: bool | Scalar = True,
    ) -> Any:
        ser = self.column
        return self._to_scalar(
            ser.std(ddof=correction),
        )

    def var(
        self,
        *,
        correction: float | Scalar | NullType = 1.0,
        skip_nulls: bool | Scalar = True,
    ) -> Any:
        ser = self.column
        return self._to_scalar(
            ser.var(ddof=correction),
        )

    def len(self) -> Scalar:
        return len(self._series)

    def n_unique(
        self,
        *,
        skip_nulls: bool = True,
    ) -> Scalar:
        ser = self.column
        return self._to_scalar(
            ser.nunique(),
        )

    # Transformations

    def is_null(self) -> Series:
        ser = self.column
        return self._from_series(ser.isna())

    def is_nan(self) -> Series:
        ser = self.column
        if is_extension_array_dtype(ser.dtype):
            return self._from_series((ser != ser).fillna(False))  # noqa: PLR0124
        return self._from_series(ser.isna())

    def sort(
        self,
        *,
        ascending: bool = True,
        nulls_position: Literal["first", "last"] = "last",
    ) -> Series:
        ser = self.column
        if ascending:
            return self._from_series(ser.sort_values().rename(self.name))
        return self._from_series(ser.sort_values().rename(self.name)[::-1])

    def is_in(self, values: Series) -> Series:
        ser = self.column
        return self._from_series(ser.isin(validate_column_comparand(self, values)))

    def sorted_indices(
        self,
        *,
        ascending: bool = True,
        nulls_position: Literal["first", "last"] = "last",
    ) -> Series:
        ser = self.column
        if ascending:
            return self._from_series(ser.sort_values().index.to_series(name=self.name))
        return self._from_series(
            ser.sort_values().index.to_series(name=self.name)[::-1]
        )

    def unique_indices(
        self,
        *,
        skip_nulls: bool | Scalar = True,
    ) -> Series:  # pragma: no cover
        msg = "not yet supported"
        raise NotImplementedError(msg)

    def fill_nan(self, value: float | NullType | Scalar) -> Series:
        idx = self.column.index
        ser = self.column.copy()
        if is_extension_array_dtype(ser.dtype):
            if self.__column_namespace__().is_null(value):
                ser[np.isnan(ser).fillna(False).to_numpy(bool)] = pd.NA
            else:
                ser[np.isnan(ser).fillna(False).to_numpy(bool)] = value
        else:
            if self.__column_namespace__().is_null(value):
                ser[np.isnan(ser).fillna(False).to_numpy(bool)] = np.nan
            else:
                ser[np.isnan(ser).fillna(False).to_numpy(bool)] = value
        ser.index = idx
        return self._from_series(ser)

    def fill_null(
        self,
        value: Any,
    ) -> Series:
        value = validate_column_comparand(self, value)
        idx = self.column.index
        ser = self.column.copy()
        if is_extension_array_dtype(ser.dtype):
            # Mask should include NA values, but not NaN ones
            mask = ser.isna() & (~(ser != ser).fillna(False))  # noqa: PLR0124
            ser = ser.where(~mask, value)
        else:
            ser = ser.fillna(value)
        ser.index = idx
        return self._from_series(ser.rename(self.name, copy=False))

    def cumulative_sum(self, *, skip_nulls: bool | Scalar = True) -> Series:
        ser = self.column
        return self._from_series(ser.cumsum())

    def cumulative_prod(self, *, skip_nulls: bool | Scalar = True) -> Series:
        ser = self.column
        return self._from_series(ser.cumprod())

    def cumulative_max(self, *, skip_nulls: bool | Scalar = True) -> Series:
        ser = self.column
        return self._from_series(ser.cummax())

    def cumulative_min(self, *, skip_nulls: bool | Scalar = True) -> Series:
        ser = self.column
        return self._from_series(ser.cummin())

    def alias(self, name: str | Scalar) -> Series:
        ser = self.column
        return self._from_series(ser.rename(name, copy=False))

    def shift(self, offset: int | Scalar) -> Series:
        ser = self.column
        return self._from_series(ser.shift(offset))

    # Conversions

    def to_array(self) -> Any:
        ser = self.column
        return ser.to_numpy(
            dtype=NUMPY_MAPPING.get(self.column.dtype.name, self.column.dtype.name),
        )

    def cast(self, dtype: DType) -> Series:
        ser = self.column
        pandas_dtype = polars_api_compat.pandas.map_standard_dtype_to_pandas_dtype(
            dtype,
        )
        return self._from_series(ser.astype(pandas_dtype))

    # --- temporal methods ---

    def year(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.year)

    def month(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.month)

    def day(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.day)

    def hour(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.hour)

    def minute(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.minute)

    def second(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.second)

    def microsecond(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.microsecond)

    def nanosecond(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.microsecond * 1000 + ser.dt.nanosecond)

    def iso_weekday(self) -> Series:
        ser = self.column
        return self._from_series(ser.dt.weekday + 1)

    def floor(self, frequency: str) -> Series:
        frequency = (
            frequency.replace("day", "D")
            .replace("hour", "H")
            .replace("minute", "T")
            .replace("second", "S")
            .replace("millisecond", "ms")
            .replace("microsecond", "us")
            .replace("nanosecond", "ns")
        )
        ser = self.column
        return self._from_series(ser.dt.floor(frequency))

    def unix_timestamp(
        self,
        *,
        time_unit: str | Scalar = "s",
    ) -> Series:
        ser = self.column
        if ser.dt.tz is None:
            result = ser - datetime(1970, 1, 1)
        else:  # pragma: no cover (todo: tz-awareness)
            result = ser.dt.tz_convert("UTC").dt.tz_localize(None) - datetime(
                1970, 1, 1
            )
        if time_unit == "s":
            result = pd.Series(
                np.floor(result.dt.total_seconds().astype("float64")),
                name=ser.name,
            )
        elif time_unit == "ms":
            result = pd.Series(
                np.floor(
                    np.floor(result.dt.total_seconds()) * 1000
                    + result.dt.microseconds // 1000,
                ),
                name=ser.name,
            )
        elif time_unit == "us":
            result = pd.Series(
                np.floor(result.dt.total_seconds()) * 1_000_000
                + result.dt.microseconds,
                name=ser.name,
            )
        elif time_unit == "ns":
            result = pd.Series(
                (
                    np.floor(result.dt.total_seconds()).astype("Int64") * 1_000_000
                    + result.dt.microseconds.astype("Int64")
                )
                * 1000
                + result.dt.nanoseconds.astype("Int64"),
                name=ser.name,
            )
        else:  # pragma: no cover
            msg = "Got invalid time_unit"
            raise AssertionError(msg)
        return self._from_series(result)