from datetime import date

"""This file should have attributes that are specific to BCPP.

Dates: Dates specific to a BHS campaign.
       These dates need to be set for each campaign.
       See also bcpp_household.mappers
"""


BHS_START_DATE = date(2014, 8, 27)
BHS_FULL_ENROLLMENT_DATE = date(2014, 10, 13)
BHS_END_DATE = date(2014, 10, 31)
SMC_START_DATE = date(2014, 10, 27)  # referenced by bcpp mappers
SMC_ECC_START_DATE = date(2014, 10, 29)  # referenced by bcpp mappers

MAX_HOUSEHOLDS_PER_PLOT = 9  # see plot models