import pandera as pa
from pandera.typing import Series


class CovariatesCentralRateOfMortality(pa.DataFrameModel):
    """
    Covariates to predict the Central Rate of Mortality
    """