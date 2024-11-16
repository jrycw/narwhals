from __future__ import annotations

import pytest

import narwhals.stable.v1 as nw
from tests.utils import PANDAS_VERSION
from tests.utils import PYARROW_VERSION
from tests.utils import Constructor
from tests.utils import ConstructorEager
from tests.utils import assert_equal_data

data = {"a": [1, 3, None, 2]}

expected = {
    "cum_max": [1, 3, None, 3],
    "reverse_cum_max": [3, 3, None, 2],
}


def test_cum_max_expr(request: pytest.FixtureRequest, constructor: Constructor) -> None:
    if "dask" in str(constructor):
        request.applymarker(pytest.mark.xfail)

    if PYARROW_VERSION < (13, 0, 0) and "pyarrow_table" in str(constructor):
        request.applymarker(pytest.mark.xfail)

    if PANDAS_VERSION < (2, 1) and "pandas_pyarrow" in str(constructor):
        request.applymarker(pytest.mark.xfail)

    df = nw.from_native(constructor(data))
    result = df.select(
        cum_max=nw.col("a").cum_max(),
        reverse_cum_max=nw.col("a").cum_max(reverse=True),
    )

    assert_equal_data(result, expected)


def test_cum_max_series(
    request: pytest.FixtureRequest, constructor_eager: ConstructorEager
) -> None:
    if PYARROW_VERSION < (13, 0, 0) and "pyarrow_table" in str(constructor_eager):
        request.applymarker(pytest.mark.xfail)

    if PANDAS_VERSION < (2, 1) and "pandas_pyarrow" in str(constructor_eager):
        request.applymarker(pytest.mark.xfail)

    df = nw.from_native(constructor_eager(data), eager_only=True)
    result = df.select(
        cum_max=df["a"].cum_max(),
        reverse_cum_max=df["a"].cum_max(reverse=True),
    )
    assert_equal_data(result, expected)