import pandas as pd
from datetime import datetime

import ncmp_inyear_code.parameters_inyear as param
from ncmp_inyear_code.utilities.export_inyear import export_excel_data


def create_table_ethnicity_imd(df_pupils_import, df_pupils_compyear,
                               df_ethnicity_ref,
                               academicyear,
                               outputpath):
    """
    Creates the data for the ethnicity and IMD in year tables and outputs it to
    the Excel source data file

    Parameters:
        df_pupils_import:
            imported pupil data
        df_pupils_compyear:
            imported data for comparison year
        df_ethnicity_ref:
            imported ethnicity reference data
        academicyear:
            current academic year
        outputpath:
            output filepath for export

    Returns:
        None
    """

    print("table_ethnicity_imd - processing pupil data")

    df_thisyear = df_pupils_import.copy()

    # Add year ref columns
    df_thisyear["AcademicYear"] = academicyear  # specify current academic year
    df_thisyear["YearRef"] = "ThisYear"  # reference for current academic year

    # Rename column names to match SQL
    old_text = ["SubmitterLocalAuthorityCode", "SubmitterLocalAuthorityName",
                "PupilIndexOfMultipleDeprivationDecile"]
    new_text = ["OrgCode", "OrgName", "PupilIndexOfMultipleDeprivationD"]

    for old_text, new_text in zip(old_text, new_text):
        df_thisyear.columns = df_thisyear.columns.str.replace(old_text, new_text)

    # Convert data types
    df_thisyear['OrgCode'] = df_thisyear['OrgCode'].apply(str)
    df_thisyear['SchoolYear'] = df_thisyear['SchoolYear'].apply(str)

    df_compyear = df_pupils_compyear.copy()

    # Combine and transform data
    print("table_ethnicity_imd - combining and transforming data")

    df_compyear["YearRef"] = "CompYear"  # reference for comparison academic year

    # Append ethnicity data to comp data
    df_compyear = pd.merge(df_compyear, df_ethnicity_ref, how="left",
                           left_on=["NhsEthnicityCode"],
                           right_on=["Value"])

    # Append the cleaned datasets
    df = df_thisyear.append([df_compyear])

    # Fill nan in the key variables with "Not stated"
    df["NcmpEthnicityCode"].fillna("Not stated", inplace=True)
    df["NhsEthnicityDescription"].fillna("Not stated", inplace=True)
    df["PupilIndexOfMultipleDeprivationD"].fillna("Not stated", inplace=True)

    # Create table outputs
    def pupil_keygroups(df, breakdowns, countcol):
        measured = df[["SchoolYear",
                       "NcmpSystemId",
                       "YearRef"]].groupby(["SchoolYear",
                                            "YearRef"]).count().reset_index()

        measured = measured.rename(columns={"NcmpSystemId": "Total"})
        measured["SchoolYear"] = measured["SchoolYear"].apply(str)

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

        subgroup["PercChange"] = ((subgroup["ValueThisYear"] -
                                   subgroup["ValueCompYear"])
                                  / subgroup["ValueCompYear"])*100

        subgroup["PercChangeTotal"] = ((subgroup["TotalThisYear"] -
                                        subgroup["TotalCompYear"])
                                       / subgroup["TotalCompYear"])*100

        return subgroup

    # Create IMD decile data
    breakdowns = ["SchoolYear",  "PupilIndexOfMultipleDeprivationD", "YearRef"]
    countcol = ["NcmpSystemId"]

    df_imd = pupil_keygroups(df, breakdowns, countcol)

    # Create ethnicity description data
    breakdowns = ["SchoolYear", "NhsEthnicityDescription",  "YearRef"]
    countcol = ["NcmpSystemId"]

    df_ethnicitydesc = pupil_keygroups(df, breakdowns, countcol)

    # Create ethnicity code data
    breakdowns = ["SchoolYear", "NcmpEthnicityCode", "YearRef"]
    countcol = ["NcmpSystemId"]

    df_ethnicitycode = pupil_keygroups(df, breakdowns, countcol)

    # Add pupil extract date to outputs
    for df in [df_imd, df_ethnicitydesc, df_ethnicitycode]:
        df["PupilExtractDate"] = datetime.strptime(param.PUPILS_FILE[27:35],
                                                   "%d%m%Y").date()

    # Export to Excel
    export_excel_data(df=df_imd,
                      sheet="IMD",
                      file_path=outputpath)

    export_excel_data(df=df_ethnicitydesc,
                      sheet="EthnicityDes",
                      file_path=outputpath)

    export_excel_data(df=df_ethnicitycode,
                      sheet="EthnicityCode",
                      file_path=outputpath)
