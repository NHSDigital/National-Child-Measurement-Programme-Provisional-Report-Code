import pandas as pd

import ncmp_inyear_code.utilities.data_connections as dbc


"""IMPORT LA DATA FUNCTIONS"""


def import_LA_DQ_data(file_path):
    """
    This function will import the LA DQ data from the specified location.
    It will only import the specified columns and shortens column names
    for easier processing
    It also excludes City of London (714) and Isles of Scilly (906)
    from the dataset as their data are submitted by Hackney and Cornwall
    respectively.

    Parameters:
        file_path:
            the full file path and name

    Returns:
        Dataframe with shortened column names and specified columns only

    """
    # Import LA data - select only columns required for process
    print("import_inyeardata - importing LA data quality data")

    import_cols = ["LocalAuthorityCode", "PercentageBlankNhsNumber",
                   "PercentageBlankPostcode", "PercentageDateOfMeasurementAugust",
                   "PercentageDateOfMeasurementWeekend", "PercentageEthnicGroupAsian",
                   "PercentageEthnicGroupBlack", "PercentageEthnicGroupChinese",
                   "PercentageEthnicGroupMixed", "PercentageEthnicGroupOther",
                   "PercentageEthnicGroupUnknown", "PercentageEthnicGroupWhite",
                   "PercentageExtremeBmi", "PercentageExtremeHeight",
                   "PercentageExtremeWeight", "PercentageHalfNumberHeights",
                   "PercentageHalfNumberWeights", "PercentagePostcodeSameAsSchool",
                   "PercentageWholeNumberHeights", "PercentageWholeNumberWeights",
                   "PercentageYear6", "PercentageYear6Female", "PercentageYear6Male",
                   "PercentageYearR", "PercentageYearRFemale", "PercentageYearRMale",
                   "TotalEligibleMeasuredYear6", "TotalEligibleMeasuredYearR"]

    df_la_import = pd.read_csv(file_path, usecols=import_cols)

    # Shorten column names
    old_text = ["LocalAuthority", "Percentage", "Postcode", "DateOfMeasurement",
                "Eligible", "Measured", "Year"]

    new_text = ["LA", "Perc", "Pcode", "DOM", "Elig", "Meas", "Yr"]

    for old_text, new_text in zip(old_text, new_text):
        df_la_import.columns = df_la_import.columns.str.replace(old_text,
                                                                new_text)

    # Exclude City of London (714) and Isles of Scilly (906)
    df_la_import = df_la_import[~df_la_import["LACode"].isin(["714", "906"])]

    return df_la_import


def import_LA_compyear(compyear):
    """
    This function will import the LA data for comparison with the LA DQ import
    for this year, from the specified location, based on the query
    referenced below

    Parameters:
        compyear:
            defines which year to use in the SQL query for filtering

    Returns:
        Dataframe with the extracted SQL data for the compyear specified
    """
    print("import_inyeardata - importing LA comparison data")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_la_compyear.sql", "r") as sql_file:
        data = sql_file.read()

    data = data.replace("<IY_COMPYEAR>", compyear)

    # Get SQL data
    df_la_compyear = dbc.df_from_sql(data, server, database)

    return df_la_compyear

"""IMPORT PUPIL DATA FUNCTIONS"""


def import_pupils_data(file_path):
    """
    This function will import the pupil level data from the specified location.
    It will only import the specified columns, with data for NCMP schools that
    have provided BMI measurements.
    It will also update 'very overweight' to 'obese' for reporting purposes

    Parameters:
        file_path:
            the full file path and name

    Returns:
        Dataframe with specified columns, for NCMP schools with BMI data
        and 'very overweight' updated to 'obese'
    """
    # Import pupil data - select only columns required for process
    print("import_inyeardata - importing pupils data")

    import_cols = ["Bmi", "BmiPopulationCategory", "BmiPScore",
                   "GenderCode",
                   "NcmpEthnicityCode", "NcmpSchoolStatus", "NcmpSystemId",
                   "NhsEthnicityDescription",
                   "PupilIndexOfMultipleDeprivationDecile",
                   "SchoolIndexOfMultipleDeprivationDecile",
                   "SchoolLowerSuperOutputArea2011",
                   "SchoolUrn", "SchoolYear", "SubmitterLocalAuthorityCode",
                   "SubmitterLocalAuthorityName"]

    df_pupils_import = pd.read_csv(file_path, usecols=import_cols)

    # Filter for NCMP schools that have submitted BMI data
    df_pupils_import = df_pupils_import[(df_pupils_import["Bmi"].notnull()) &
                                        (df_pupils_import["NcmpSchoolStatus"] == "NCMP")].copy()

    # Update 'very overweight' to 'obese'
    df_pupils_import.loc[df_pupils_import["BmiPopulationCategory"] == "very overweight",
                         "BmiPopulationCategory"] = "obese"

    return df_pupils_import


def import_pupils_compyear(compyear):
    """
    This function will import the data for comparison with the pupils data
    import for this year, from the specified location, based on the query
    referenced below
    It will also update 'very overweight' to 'obese' for reporting purposes

    Parameters:
        compyear:
            defines which year to use in the SQL query for filtering

    Returns:
        Dataframe with the extracted SQL data for the compyear specified
        and 'very overweight' updated to 'obese'
    """
    print("import_inyeardata - importing pupils comparison data")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_pupils_compyear.sql", "r") as sql_file:
        data = sql_file.read()

    data = data.replace("<IY_COMPYEAR>", compyear)

    # Get SQL data
    df_pupils_compyear = dbc.df_from_sql(data, server, database)

    # Update 'very overweight' to 'obese'
    df_pupils_compyear.loc[df_pupils_compyear["BmiPopulationCategory"] == "very overweight",
                           "BmiPopulationCategory"] = "obese"

    return df_pupils_compyear


def import_pupils_baseyears(baseyears):
    """
    This function will import the data for the years required to create the
    base data for the weighting table output, from the specified location,
    based on the query referenced below
    It will also update 'very overweight' to 'obese' for reporting purposes

    Parameters:
        baseyears:
            defines which years to use in the SQL query for filtering

    Returns:
        Dataframe with the extracted SQL data for the base years specified
        and 'very overweight' updated to 'obese'
    """
    print("import_inyeardata - importing base years data for weighting")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_pupils_baseyears.sql", "r") as sql_file:
        data = sql_file.read()

    data = data.replace("<IY_BASEYEARS>", baseyears)

    # Get SQL data
    df_pupils_baseyears = dbc.df_from_sql(data, server, database)

    # Update 'very overweight' to 'obese'
    df_pupils_baseyears.loc[df_pupils_baseyears["BmiPopulationCategory"] == "very overweight",
                            "BmiPopulationCategory"] = "obese"

    return df_pupils_baseyears


"""IMPORT REFERENCE DATA FUNCTIONS"""


def import_ethnicity_ref():
    """
    This function will import the ethnicity reference data from the
    from the specified location

    Parameters:
        None

    Returns:
        Dataframe with ethnicity reference data
    """
    print("import_inyeardata - importing ethnicity reference data")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_ethnicity_ref.sql", "r") as sql_file:
        data = sql_file.read()

    # Get SQL data
    df_ethnicity_ref = dbc.df_from_sql(data, server, database)

    return df_ethnicity_ref


def import_lsoa_ref():
    """
    This function will import the latest LSOA reference data from the
    from the specified location

    Parameters:
        None

    Returns:
        Dataframe with the latest LSOA reference data
    """
    print("import_inyeardata - importing LSOA reference data")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_lsoa_ref.sql", "r") as sql_file:
        data = sql_file.read()

    # Get SQL data
    df_lsoa_ref = dbc.df_from_sql(data, server, database)

    # Remove duplicates from LSOA reference data, keep only the last entry
    df_lsoa_ref = df_lsoa_ref.drop_duplicates(subset=["LSOACD"], keep='last')

    return df_lsoa_ref


def import_la_e07_ref():
    """
    This function will import the latest E07 LA reference data from the
    from the specified location

    Parameters:
        None

    Returns:
        Dataframe with the latest E07 LA reference data

    """
    print("import_inyeardata - importing E07 LA reference data")

    server = "SERVER"
    database = "DATABASE"

    sql_folder = r"ncmp_inyear_code\sql_code"

    with open(sql_folder + "\query_la_e07_ref.sql", "r") as sql_file:
        data = sql_file.read()

    # Get SQL data
    df_la_e07_ref = dbc.df_from_sql(data, server, database)

    # Remove duplicates from LSOA reference data, keep only the last entry
    df_la_e07_ref = df_la_e07_ref.drop_duplicates(subset=["GEOGRAPHY_CODE"],
                                                  keep='last')

    return df_la_e07_ref
