import pandas as pd
from datetime import datetime

import ncmp_inyear_code.parameters_inyear as param
from ncmp_inyear_code.utilities.export_inyear import export_excel_data


def create_table_school_cohort(df_pupils_import, df_pupils_compyear,
                               academicyear, outputpath):
    """
    Creates the data for the school cohort table and outputs it to the Excel
    source data file

    Parameters:
        df_pupils_import:
            imported pupil data
        df_pupils_compyear:
            imported data for comparison year
        academicyear:
            current academic year
        outputpath:
            output filepath for export

    Returns:
        None
    """

    print("table_schoolcohort - processing pupil data")

    df_thisyear = df_pupils_import.copy()

    # This year - convert data types
    df_thisyear['SchoolUrn'] = df_thisyear['SchoolUrn'].apply(str)
    df_thisyear['SchoolYear'] = df_thisyear['SchoolYear'].apply(str)

    # This year - add calculated columns
    df_thisyear["AcademicYear"] = param.IY_THISYEAR  # specify current academic year
    df_thisyear["YearRef"] = "ThisYear"  # reference for current academic year
    df_thisyear["CohortLink"] = (df_thisyear["SchoolUrn"] +
                                 df_thisyear["SchoolYear"])  # add cohort link of urn and school year

    # This year - rename column names to match SQL
    old_text = ["SubmitterLocalAuthorityCode", "SubmitterLocalAuthorityName",
                "PupilIndexOfMultipleDeprivationDecile"]

    new_text = ["OrgCode", "OrgName", "PupilIndexOfMultipleDeprivationD"]

    for old_text, new_text in zip(old_text, new_text):
        df_thisyear.columns = df_thisyear.columns.str.replace(old_text, new_text)

    # This year - create count of measured by school and school year
    df_thisyear["SchNoMeasured"] = df_thisyear.groupby(["SchoolUrn",
                                                        "SchoolYear"]
                                                       ).NcmpSystemId.transform("count")

    # This year - include only schools with submission >=10
    df_thisyear = df_thisyear.loc[df_thisyear["SchNoMeasured"] >= 10]

    # Combine and transform data
    print("table_schoolcohort - combining and transforming data")

    # Comparison year - convert data types
    df_compyear = df_pupils_compyear.copy()

    df_compyear["SchoolUrn"] = df_compyear["SchoolUrn"].apply(str)
    df_compyear["SchoolYear"] = df_compyear["SchoolYear"].apply(str)

    # Comp year - add reference fields
    df_compyear["YearRef"] = "CompYear"   # reference for comparison academic year
    df_compyear["CohortLink"] = (df_compyear["SchoolUrn"] +
                                 df_compyear["SchoolYear"])

    # Comp year - create count of measured by school and school year
    df_compyear["SchNoMeasured"] = df_compyear.groupby(["SchoolUrn",
                                                        "SchoolYear"]
                                                       ).NcmpSystemId.transform("count")

    # Comp year - include only schools with submission >=10
    df_compyear = df_compyear.loc[df_compyear["SchNoMeasured"] >= 10]

    # Append datasets for both years
    df = df_thisyear.append([df_compyear])

    # Create the school cohort outputs

    # Get a list of the school URNs for this year
    school_set_thisyear = list(set(df_thisyear["CohortLink"]))

    # Create list of cohort schools - schools submitted this year and comparison year
    cohort_compyear = df_compyear[["CohortLink"]].query("CohortLink in @school_set_thisyear")
    school_set_cohort = list(set(cohort_compyear["CohortLink"]))

    # Filter data to include only schools in the school cohort
    df_school_cohort = df.query("CohortLink in @school_set_cohort")

    # Filter out data for those not in the school cohort
    df_only = df.query("CohortLink not in @school_set_cohort")

    # Create table outputs
    def pupil_keygroups(df, breakdowns, countcol):
        measured = df[["SchoolYear",
                       "NcmpSystemId",
                       "YearRef"]].groupby(["SchoolYear",
                                            "YearRef"]).count().reset_index()

        measured = measured.rename(columns={"NcmpSystemId": "Total"})

        subgroup = df[breakdowns + countcol].groupby([*breakdowns]).count().reset_index()
        subgroup = subgroup.rename(columns={"NcmpSystemId": "Value"})
        subgroup["SchoolYear"] = subgroup["SchoolYear"].apply(str)

        subgroup = pd.merge(subgroup, measured,  how="left",
                            left_on=["YearRef",  "SchoolYear"],
                            right_on=["YearRef", "SchoolYear"])

        subgroup["Proportion"] = subgroup["Value"]/subgroup["Total"] * 100

        subgroup = pd.pivot_table(subgroup,
                                  values=["Total", "Proportion", "Value"],
                                  index=breakdowns[:-1],
                                  columns="YearRef").reset_index()

        subgroup.columns = [s1 + str(s2) for (s1, s2) in subgroup.columns.tolist()]

        subgroup["PercPointChange"] = (subgroup["ProportionThisYear"] -
                                       subgroup["ProportionCompYear"])

        return subgroup

    # Create outputs
    breakdowns = ["SchoolYear",  "BmiPopulationCategory", "YearRef"]
    countcol = ["NcmpSystemId"]

    df_bmi_all = pupil_keygroups(df, breakdowns, countcol)
    df_bmi_cohort = pupil_keygroups(df_school_cohort, breakdowns, countcol)
    df_bmi_only = pupil_keygroups(df_only, breakdowns, countcol)

    # Add table reference
    df_bmi_all["TableRef"] = "All"
    df_bmi_cohort["TableRef"] = "School Cohort"
    df_bmi_only["TableRef"] = "Only"

    # Combine data
    df_bmi_school_cohort = df_bmi_all.append([df_bmi_cohort, df_bmi_only])

    # Add pupil extract date
    df_bmi_school_cohort["PupilExtractDate"] = datetime.strptime(param.PUPILS_FILE[27:35],
                                                                 "%d%m%Y").date()

    # Export to Excel
    export_excel_data(df_bmi_school_cohort, "CohortAnalysis", outputpath)
