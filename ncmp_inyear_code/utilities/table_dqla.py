import pandas as pd
import numpy as np
from datetime import datetime

import ncmp_inyear_code.parameters_inyear as param
from ncmp_inyear_code.utilities.export_inyear import export_excel_data


def create_table_dqla(df_la_import, df_la_compyear, df_la_lookups,
                      laexclude, outputpath):
    """
    Creates the output needed to feed the LA data quality tables for the
    in year publication and outputs it to the Excel source data file

    Parameters:
        df_la_import:
            imported LA data
        df_la_compyear:
            LA data for comparison year
        df_la_lookups:
            LA to reporting region lookups
        laexclude:
            list of LAs to exclude when calculating LA level indicators
        outputpath:
            filepath to output file for export

    Returns:
        None
    """
    print("table_dqla - combining and transforming data")

    df_thisyear = df_la_import.copy()
    df_compyear = df_la_compyear.copy()

    # Add total measured to this year
    df_thisyear["TotalEligMeas"] = (df_thisyear["TotalEligMeasYrR"] +
                                    df_thisyear["TotalEligMeasYr6"])

    # Comparison year - group to show number measured by school year and LA
    df_compyear = df_compyear.groupby(by=["AcademicYear", "SchoolYear",
                                          "OrgCode"]).count()
    df_compyear.reset_index(inplace=True)

    # Comp year - pivot so one column per school year and rename columns
    df_compyear = df_compyear.pivot(index="OrgCode", columns="SchoolYear",
                                    values="NcmpSystemId")
    df_compyear.reset_index(inplace=True)

    df_compyear.rename(columns={"R": "MeasuredYrRCompYr",
                                "6": "MeasuredYr6CompYr"}, inplace=True)

    # Comp year - add measured total
    df_compyear["MeasuredCompYr"] = (df_compyear["MeasuredYrRCompYr"] +
                                     df_compyear["MeasuredYr6CompYr"])

    # Combine this year's and comparison year's data
    df = pd.merge(df_thisyear, df_compyear,
                  how="outer",
                  left_on="LACode",
                  right_on="OrgCode")

    # Calculate indicator - percentage of records sharing the same ethnicity
    def ind_perc_same_eth(df, ethcols, outputcol):

        df[outputcol] = 0
        df.loc[df[ethcols].eq(100).any(axis=1), outputcol] = 100
        df.loc[(df["PercYrR"].isnull()) & (df["PercYr6"].isnull()), outputcol] = np.nan

        return df

    ethcols = ["PercEthnicGroupAsian", "PercEthnicGroupBlack",
               "PercEthnicGroupChinese", "PercEthnicGroupMixed",
               "PercEthnicGroupOther", "PercEthnicGroupWhite"]

    df = ind_perc_same_eth(df, ethcols, outputcol="PercSameEth")

    # Calculate indicator - measured this year as proportion of submitted in comp year
    # Set to na for LAs marked as exclude in LA_IY_COMPEXCLUDE parameter
    def ind_meas_prop_subcompyr(df, num, denom, outputcol, roundtodp,
                                laexclude):

        df[outputcol] = round((df[num]/df[denom])*100, roundtodp)
        df.loc[df["LACode"].isin(laexclude), outputcol] = np.nan

        return df

    df = ind_meas_prop_subcompyr(df, "TotalEligMeas", "MeasuredCompYr",
                                 "PropMeasVsSubPrevTotal", 1, laexclude)

    df = ind_meas_prop_subcompyr(df, "TotalEligMeasYrR", "MeasuredYrRCompYr",
                                 "PropMeasVsSubPrevYrR", 1, laexclude)

    df = ind_meas_prop_subcompyr(df, "TotalEligMeasYr6", "MeasuredYr6CompYr",
                                 "PropMeasVsSubPrevYr6", 1, laexclude)

    # Add regions to data
    df = pd.merge(df, df_la_lookups, how="left", on="LACode")

    # Create LA submission status data by region and school year
    print("table_dqla - generating LA submission status by region output")

    def create_sub_status(df, schyears):

        df_sub = []

        for year in schyears:

            # Add submission status to main dataframe
            df["SubStatus"+year] = "No data"

            df.loc[df["TotalEligMeas"+year] > 0, "SubStatus"+year] = "Some data"

            # Copy and regroup by status
            df_year = df.copy()

            df_year = df_year.groupby(by=["PHERegionalOffice",
                                          "SubStatus"+year]).size().reset_index()

            df_year.rename(columns={"SubStatus" + year: "Indicator", 0: "Value"},
                           inplace=True)

            df_year["Grouping"] = year

            df_year["TableRef"] = "A1: Summary of LAs submitting"

            df_sub.append(df_year)

        # Append school year data
        df_sub = pd.concat(df_sub)

        return df_sub

    df_sub = create_sub_status(df, schyears=["YrR", "Yr6"])

    # Create count of LAs in each measured this year vs submitted comp year proportion grouping
    print("table_dqla - generating LAs with measurements vs those submitted in comparator year")

    def create_la_prop_count(df, schyears, compyear=param.IY_COMPYEAR[3:10]):

        df_prop = []

        for year in schyears:

            propmeas = "PropMeasVsSubPrev"+year
            substatus = "SubStatus"+year
            propmeasgrp = "PropMeasVsSubPrevGrp"+year

            df_year = df[["PHERegionalOffice",
                          "LACode",
                          propmeas,
                          substatus]].copy()

            # Add groupings by school year
            df_year.loc[(df_year[propmeas] > 0)
                        & (df_year[propmeas] < 50)
                        & (df_year[substatus] == "Some data"),
                        propmeasgrp] = "<50%"

            df_year.loc[(df_year[propmeas] >= 50)
                        & (df_year[propmeas] < 75)
                        & (df_year[substatus] == "Some data"),
                        propmeasgrp] = "50 to <75%"

            df_year.loc[(df_year[propmeas] >= 75)
                        & (df_year[substatus] == "Some data"),
                        propmeasgrp] = "75% or over"

            df_year.loc[(df_year[propmeas].isnull())
                        & (df_year[substatus] == "Some data"),
                        propmeasgrp] = "No comparable data"

            # Add counts by school year and proportion grouping
            df_year = df_year.groupby(by=[propmeasgrp]).size().reset_index()
            df_year.rename(columns={propmeasgrp: "Indicator", 0: "Value"}, inplace=True)
            df_year["Grouping"] = year

            df_year["TableRef"] = "A2: LA measurement proportions vs comparison year"

            # Add comparison year for reference
            df_year["ComparisonYear"] = compyear

            # Append school year data
            df_prop.append(df_year)

        df_prop = pd.concat(df_prop)

        return df_prop

    df_prop = create_la_prop_count(df, schyears=["YrR", "Yr6"])

    # Create DQ indicators for England output
    print("table_dqla - generating national data quality indicators")

    def createengindicators(df):

        # Calculate numerators from this year's percentages for England calc
        perccols = ["PercYrRMale", "PercYrRFemale", "PercYr6Male",
                    "PercYr6Female", "PercBlankPcode", "PercPcodeSameAsSchool",
                    "PercEthnicGroupUnknown", "PercBlankNhsNumber", "PercSameEth",
                    "PercExtremeHeight", "PercExtremeWeight", "PercExtremeBmi",
                    "PercWholeNumberHeights", "PercWholeNumberWeights",
                    "PercHalfNumberHeights", "PercHalfNumberWeights",
                    "PercDOMWeekend"]

        denomcols = ["TotalEligMeasYrR", "TotalEligMeasYrR", "TotalEligMeasYr6",
                     "TotalEligMeasYr6", "TotalEligMeas", "TotalEligMeas",
                     "TotalEligMeas", "TotalEligMeas", "TotalEligMeas",
                     "TotalEligMeas", "TotalEligMeas", "TotalEligMeas",
                     "TotalEligMeas", "TotalEligMeas",
                     "TotalEligMeas", "TotalEligMeas",
                     "TotalEligMeas"]

        for perc, denom in zip(perccols, denomcols):
            df[perc.replace("Perc", "Num")] = (df[denom]/100)*df[perc]

        # Calculate England data
        df_eng = df[["TotalEligMeas", "TotalEligMeasYrR", "TotalEligMeasYr6",
                     "MeasuredCompYr", "MeasuredYrRCompYr", "MeasuredYr6CompYr",
                     "NumYrRMale", "NumYrRFemale", "NumYr6Male", "NumYr6Female",
                     "NumBlankPcode", "NumPcodeSameAsSchool", "NumEthnicGroupUnknown",
                     "NumBlankNhsNumber", "NumSameEth", "NumExtremeHeight",
                     "NumExtremeWeight", "NumExtremeBmi", "NumWholeNumberHeights",
                     "NumWholeNumberWeights", "NumHalfNumberHeights",
                     "NumHalfNumberWeights", "NumDOMWeekend"]].sum().reset_index()

        # Transpose and make first row column headers
        df_eng = df_eng.T
        df_eng.columns = df_eng.iloc[0]
        df_eng = df_eng[1:]

        # Calculate new percentages, to 1 decimal place, using dictionary of definitions
        perccalcs = {
            "PropMeasVsSubPrevTotal": "df_eng['TotalEligMeas']/df_eng['MeasuredCompYr']*100",
            "PropMeasVsSubPrevYrR": "df_eng['TotalEligMeasYrR']/df_eng['MeasuredYrRCompYr']*100",
            "PropMeasVsSubPrevYr6": "df_eng['TotalEligMeasYr6']/df_eng['MeasuredYr6CompYr']*100",
            "PercYrR": "df_eng['TotalEligMeasYrR']/df_eng['TotalEligMeas']*100",
            "PercYr6": "df_eng['TotalEligMeasYr6']/df_eng['TotalEligMeas']*100",
            "PercYrRMale": "df_eng['NumYrRMale']/df_eng['TotalEligMeasYrR']*100",
            "PercYrRFemale": "df_eng['NumYrRFemale']/df_eng['TotalEligMeasYrR']*100",
            "PercYr6Male": "df_eng['NumYr6Male']/df_eng['TotalEligMeasYr6']*100",
            "PercYr6Female": "df_eng['NumYr6Female']/df_eng['TotalEligMeasYr6']*100",
            "PercBlankPcode": "df_eng['NumBlankPcode']/df_eng['TotalEligMeas']*100",
            "PercPcodeSameAsSchool": "df_eng['NumPcodeSameAsSchool']/df_eng['TotalEligMeas']*100",
            "PercEthnicGroupUnknown": "df_eng['NumEthnicGroupUnknown']/df_eng['TotalEligMeas']*100",
            "PercSameEth": "df_eng['NumSameEth']/df_eng['TotalEligMeas']*100",
            "PercBlankNhsNumber": "df_eng['NumBlankNhsNumber']/df_eng['TotalEligMeas']*100",
            "PercExtremeHeight": "df_eng['NumExtremeHeight']/df_eng['TotalEligMeas']*100",
            "PercExtremeWeight": "df_eng['NumExtremeWeight']/df_eng['TotalEligMeas']*100",
            "PercExtremeBmi": "df_eng['NumExtremeBmi']/df_eng['TotalEligMeas']*100",
            "PercWholeNumberHeights": "df_eng['NumWholeNumberHeights']/df_eng['TotalEligMeas']*100",
            "PercWholeNumberWeights": "df_eng['NumWholeNumberWeights']/df_eng['TotalEligMeas']*100",
            "PercHalfNumberHeights": "df_eng['NumHalfNumberHeights']/df_eng['TotalEligMeas']*100",
            "PercHalfNumberWeights": "df_eng['NumHalfNumberWeights']/df_eng['TotalEligMeas']*100",
            "PercDOMWeekend": "df_eng['NumDOMWeekend']/df_eng['TotalEligMeas']*100",
            }

        for key in perccalcs:
            df_eng[key] = eval(perccalcs[key])
            df_eng[key] = df_eng[key].astype(float).round(1)

        # Reformat
        df_eng = df_eng[["TotalEligMeas", "TotalEligMeasYrR", "TotalEligMeasYr6",
                         "PropMeasVsSubPrevTotal", "PropMeasVsSubPrevYrR",
                         "PropMeasVsSubPrevYr6", "PercYrR", "PercYr6",
                         "PercYrRMale", "PercYrRFemale", "PercYr6Male",
                         "PercYr6Female", "PercBlankPcode", "PercPcodeSameAsSchool",
                         "PercEthnicGroupUnknown", "PercSameEth",
                         "PercBlankNhsNumber", "PercExtremeHeight",
                         "PercExtremeWeight", "PercExtremeBmi",
                         "PercWholeNumberHeights", "PercWholeNumberWeights",
                         "PercHalfNumberHeights", "PercHalfNumberWeights",
                         "PercDOMWeekend"]]

        df_eng = df_eng.copy().T.reset_index()
        df_eng.columns = ["Indicator", "Value"]
        df_eng["TableRef"] = "A3: England DQ indicators"

        return df_eng

    df_eng = createengindicators(df)

    # Combine outputs
    df_dqla = pd.concat([df_sub, df_prop, df_eng])
    df_dqla["PHERegionalOffice"].fillna("England", inplace=True)

    df_dqla = df_dqla[["TableRef", "Indicator", "Grouping",
                       "PHERegionalOffice", "Value", "ComparisonYear"]]

    # Add extract date
    df_dqla["LADQExtractDate"] = datetime.strptime(param.LA_IY_FILE[34:42],
                                                   "%d%m%Y").date()

    export_excel_data(df_dqla, "LA_InYear", outputpath)
