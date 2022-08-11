import pandas as pd
import numpy as np
import scipy.stats
from datetime import datetime

import ncmp_inyear_code.parameters_inyear as param
from ncmp_inyear_code.utilities.export_inyear import export_excel_data


def create_table_bmi_prev(df_pupils_import, outputpath):
    """
    Creates the data for the BMI prevalence tables and outputs it to
    the Excel source data file

    Parameters:
        df_pupils_data:
            imported pupil data
        outputpath:
            filepath to output file for export

    Returns:
        None
    """

    print("inyear_bmi_prev - processing pupil data")

    df = df_pupils_import.copy()

    # Recode gender
    df.loc[df["GenderCode"] == "ge01", "Gender"] = "male"
    df.loc[df["GenderCode"] == "ge02", "Gender"] = "female"

    # Update data types
    df['SchoolYear'] = df['SchoolYear'].apply(str)

    # Group by categories and count
    def groupcount(df, groupcols, countcol):
        """ Groups by selected columns (groupcols) and counts
        selected column (countcol)"""
        df = df[groupcols + [countcol]].groupby(by=groupcols).count()
        df.rename(columns={countcol: "Count"}, inplace=True)
        df.reset_index(inplace=True)

        return df

    # Group and count by existing categories in dataset
    groupcols = ["SchoolYear", "Gender", "BmiPopulationCategory"]
    countcol = "NcmpSystemId"
    df_group = groupcount(df, groupcols, countcol)

    # Create severely obese, and obese and overweight counts
    df_sevob = df[df["BmiPScore"] >= 0.996].copy()
    df_sevob["BmiPopulationCategory"] = "severely obese"
    df_sevob_group = groupcount(df_sevob, groupcols, countcol)

    df_ovob = df[df["BmiPopulationCategory"].isin(["overweight", "obese"])].copy()
    df_ovob["BmiPopulationCategory"] = "overweight or obese"
    df_ovob_group = groupcount(df_ovob, groupcols, countcol)

    # Append counts
    df_bmi_group = pd.concat([df_group, df_sevob_group, df_ovob_group])

    # Calculate prevalences and confidence intervals
    print("inyear_bmi_prev - calculating prevalences and confidence intervals")

    # Pivot so one column per category and calculate total
    df_bmi_prev = df_bmi_group.pivot(index=["SchoolYear", "Gender"],
                                     columns="BmiPopulationCategory",
                                     values="Count")

    df_bmi_prev.reset_index(inplace=True)
    df_bmi_prev["Total"] = df_bmi_prev[["underweight", "healthy weight",
                                        "overweight", "obese"]].sum(axis=1)

    # Add total row for each school year (reception/year 6)
    df_bmi_prevtot = df_bmi_prev.groupby(by="SchoolYear").sum()
    df_bmi_prevtot["Gender"] = "Both"
    df_bmi_prevtot.reset_index(inplace=True)

    # Append totals to prevalence data
    df_bmi_prev = pd.concat([df_bmi_prev, df_bmi_prevtot])

    # Calculate prevalences
    numerators = ["underweight", "healthy weight", "overweight", "obese",
                  "severely obese", "overweight or obese"]

    for numerator in numerators:
        df_bmi_prev[numerator + "_prev"] = (df_bmi_prev[numerator] /
                                            df_bmi_prev["Total"])*100

    # Calculate confidence intervals

    def calc_conf_intervals(df, observedcol, samplecol, outputformat=None):
        """ Calculates lower and upper confidence intervals for a column
        based on methodology used in NCMP annual report
        https://digital.nhs.uk/data-and-information/publications/statistical/national-child-measurement-programme/2020-21-school-year/appendices#appendix-d-confidence-intervals)

        Parameters:
            df: pandas.Dataframe
                dataframe containing columns used to calculate CIs
            observedcol:
                column with observed number for feature of interest e.g. numerator
            samplecol:
                column for sample size e.g. denominator
            outputformat:
                will output CIs as percentages if set to "percent"

        Returns:
            df: pandas.Dataframe
                Dataframe containing upper and lower confidence intervals
                for observedcol
                """

        df["r"] = df[observedcol]
        df["n"] = df[samplecol]

        df["p"] = df["r"]/df["n"]  # proportion with feature of interest
        df["q"] = 1 - df["p"]  # proportion without feature of interest
        df["z"] = scipy.stats.norm.ppf(0.975)  # 𝑧(1−∝/2) from the standard Normal distribution

        df["A"] = (2*df["r"]) + (df["z"]**2)
        df["B"] = df["z"] * np.sqrt((df["z"]**2) + (4*df["r"]*df["q"]))
        df["C"] = 2*(df["n"] + df["z"]**2)

        if outputformat == "percent":
            df[observedcol + "_ci_lower"] = (df["A"]-df["B"])/df["C"]*100
            df[observedcol + "_ci_upper"] = (df["A"]+df["B"])/df["C"]*100

        else:
            df[observedcol + "_ci_lower"] = (df["A"]-df["B"])/df["C"]
            df[observedcol + "_ci_upper"] = (df["A"]+df["B"])/df["C"]

        df.drop(columns=["r", "n", "p", "q", "z", "A", "B", "C"], inplace=True)

        return df

    observedcols = ["underweight", "healthy weight", "overweight", "obese",
                    "severely obese", "overweight or obese"]

    for observedcol in observedcols:
        calc_conf_intervals(df=df_bmi_prev, observedcol=observedcol,
                            samplecol="Total", outputformat="percent")

    df_bmi_prev = df_bmi_prev[["SchoolYear", "Gender", "underweight",
                               "underweight_prev", "underweight_ci_lower",
                               "underweight_ci_upper", "healthy weight",
                               "healthy weight_prev", "healthy weight_ci_lower",
                               "healthy weight_ci_upper", "overweight",
                               "overweight_prev", "overweight_ci_lower",
                               "overweight_ci_upper", "obese", "obese_prev",
                               "obese_ci_lower", "obese_ci_upper",
                               "severely obese", "severely obese_prev",
                               "severely obese_ci_lower",
                               "severely obese_ci_upper",
                               "overweight or obese", "overweight or obese_prev",
                               "overweight or obese_ci_lower",
                               "overweight or obese_ci_upper",
                               "Total"]].sort_values(by=(["SchoolYear", "Gender"]),
                                                     ascending=False)

    # Add extract date
    df_bmi_prev["PupilExtractDate"] = datetime.strptime(param.PUPILS_FILE[27:35],
                                                        "%d%m%Y").date()

    export_excel_data(df_bmi_prev, "BMI_Prev", outputpath)
