from enum import StrEnum, auto

import pandera as pa
from pandera import Check, Column, DataFrameSchema
from pandera.typing import Series
import numpy as np


class HelperChecks:
    """Class storing the pandera Helper Check Functions."""

    nonempty_string_check = Check(
        lambda s: s.astype(str).str.strip().str.len() > 0,
        ignore_na=True,
        error="Must be a non-empty string.",
    )

    finite_float_check = Check(
        lambda s: np.isfinite(s), ignore_na=True, error="Must be finite."
    )

    class Sex(StrEnum):
        male = auto()
        female = auto()
        other = auto()
        unknown = auto()
    _SEX = tuple(Sex)
    sex_check = Check(
        lambda s, valid_categories=_SEX: (
            s.astype(str).str.strip().str.lower().isin(valid_categories)
        ),
        error=f"Available categories: {_SEX}.",
    )

    _AGE_BASIS = (
        "exact_age",
        "age_last_birthday",
        "age_nearest_birthday",
        "age_next_birthday",
        "issue_age",
        "attained_age",
    )
    age_check = Check(
        lambda s: s.astype(str).str.strip().str.lower().isin(HelperChecks._AGE_BASIS),
        error=f"Available categories: {_AGE_BASIS}.",
    )
    
    _TERMINATION_REASON = ("death", "lapse", "surrender", "withdrawal", "maturity", "cancellation", "administrative")


class ActuarialMortalityFeatures(pa.DataFrameModel):
    """
    Covariates used to predict Mortality Rate.
    """

    policy_id: Series[str] = pa.Field(
        nullable=False, checks=[HelperChecks.nonempty_string_check]
    )
