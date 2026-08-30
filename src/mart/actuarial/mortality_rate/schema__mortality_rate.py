import pandera as pa
from pandera.typing import Check, Column, DataFrameSchema
import numpy as np


class ActuarialMortalityFeatures(pa.DataFrameModel):
    """
    Covariates used to predict Mortality Rate.
    """
    pass