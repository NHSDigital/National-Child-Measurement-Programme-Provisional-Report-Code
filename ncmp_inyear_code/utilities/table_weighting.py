import pandas as pd
from datetime import datetime

import ncmp_inyear_code.parameters_inyear as param
from ncmp_inyear_code.utilities.export_inyear import export_excel_data


def create_table_weighting(df_pupils_import, df_pupils_baseyears,
                           df_ethnicity_ref, df_lsoa_ref, df_la_e07_ref,
                           df_ethnicity_ref_ohid, df_imd_ref_ohid,
                           academicyear, compyear, outputpath):
    """
    Creates the data for the weighting table and outputs it to the Excel
    source data file

    Parameters:
        df_pupils_import:
            imported pupil data
        df_pupils_baseyears:
            imported data for base years
        df_ethnicity_ref:
            imported ethnicity reference data
        df_lsoa_ref:
            imported LSOA reference data
        df_la_e07_ref:
            imported LA reference data for E07 codes
        df_ethnicity_ref_ohid:
            imported ethnicity reference lookups from OHID
        df_imd_ref_ohid:
            imported IMD quintiles reference lookups from OHID
        academicyear:
            current academic year
        compyear:
            comparison year
        outputpath:
            output filepath for export

    Returns:
        None
    """

    print("table_weighting - processing pupil data for this year and base years")

    df_thisyear = df_pupils_import.copy()

    # This year add year reference columns
    df_thisyear["AcademicYear"] = academicyear  # specify current academic year
    df_thisyear["Year_ref"] = "ThisYear"  # specify reference current academic year

    # This year - rename column names to match SQL
    old_text = ["PupilIndexOfMultipleDeprivationDecile",
                "SchoolIndexOfMultipleDeprivationDecile"]

    new_text = ["PupilIndexOfMultipleDeprivationD",
                "SchoolIndexOfMultiDeprivationD"]

    for old_text, new_text in zip(old_text, new_text):
        df_thisyear.columns = df_thisyear.columns.str.replace(old_text, new_text)

    # Base years - add ethnicity description from ethnicity reference data
    df_baseyears = df_pupils_baseyears.copy()

    df_baseyears = pd.merge(df_baseyears,
                            df_ethnicity_ref,
                            how="left",
                            left_on=["NhsEthnicityCode"],
                            right_on=["Value"])

    # Add reference data and update data types for this year and base years
    def process_weighting(df, df_lsoa_ref, df_la_e07_ref,
                          df_ethnicity_ref_ohid, df_imd_ref_ohid):

        # Replace missing pupil IMD with school IMD
        df["ImdDecile"] = df["PupilIndexOfMultipleDeprivationD"]

        df.loc[df["ImdDecile"].isnull(),
               "ImdDecile"] = df["SchoolIndexOfMultiDeprivationD"]

        # Add latest LA codes from reference data based on school LSOA2011
        df = pd.merge(df,
                      df_lsoa_ref[["LSOACD", "LADCD"]],
                      how="left",
                      left_on=["SchoolLowerSuperOutputArea2011"],
                      right_on=["LSOACD"])

        # Add latest upper tier LA codes for E07 LAs
        df = pd.merge(df,
                      df_la_e07_ref[["PARENT_GEOGRAPHY_CODE",
                                     "GEOGRAPHY_CODE",
                                     "ENTITY_CODE"]],
                      how="left",
                      left_on=["LADCD"],
                      right_on=["GEOGRAPHY_CODE"])

        # Assign accurate upper tier LA code
        df["UpperTierLA"] = df["LADCD"]

        df.loc[df["ENTITY_CODE"] == "E07",
               "UpperTierLA"] = df["PARENT_GEOGRAPHY_CODE"]

        # Assign LAs to any URNs missing school LSOA as defined in parameters
        for key in param.URN_UPDATE_WEIGHTING_LA:
            df.loc[df["SchoolUrn"] == key,
                   "UpperTierLA"] = param.URN_UPDATE_WEIGHTING_LA[key]

        # Recode ethnicity description into 5 groups based on OHID reference
        df = pd.merge(df,
                      df_ethnicity_ref_ohid,
                      how="left",
                      left_on=["NhsEthnicityDescription"],
                      right_on=["NhsEthnicityDescription"])

        # Recode IMD decile into 5 groups (quintiles) based on OHID reference
        df = pd.merge(df,
                      df_imd_ref_ohid,
                      how="left",
                      left_on=["ImdDecile"],
                      right_on=["IMD Decile"])

        # Convert weighting variables to strings
        df = df.astype({"UpperTierLA": str, "SchoolYear": str,
                        "Ethnic Group": str, "IMD Quintile": str})

        return df

    df_thisyear = process_weighting(df_thisyear, df_lsoa_ref, df_la_e07_ref,
                                    df_ethnicity_ref_ohid, df_imd_ref_ohid)

    df_baseyears = process_weighting(df_baseyears, df_lsoa_ref, df_la_e07_ref,
                                     df_ethnicity_ref_ohid, df_imd_ref_ohid)

    # Create weightings
    print("table_weighting - creating weightings")

    # Base years - create average measured value (2016/17 to 2018/19) grouped by key variables
    df_baseyears_weight = df_baseyears[["SchoolYear",
                                        "UpperTierLA",
                                        "IMD Quintile",
                                        "Ethnic Group",
                                        "NcmpSystemId"]].groupby(["SchoolYear",
                                                                  "UpperTierLA",
                                                                  "IMD Quintile",
                                                                  "Ethnic Group"]).count().reset_index()

    # Base years - calculate average value
    df_baseyears_weight["measured_BaseYear"] = (df_baseyears_weight["NcmpSystemId"] /
                                                len(set(df_baseyears["AcademicYear"])))

    # Base years - create a link field
    df_baseyears_weight["Link_Field"] = (df_baseyears_weight["SchoolYear"] +
                                         df_baseyears_weight["UpperTierLA"] +
                                         " " +
                                         df_baseyears_weight["IMD Quintile"].astype(str) +
                                         df_baseyears_weight["Ethnic Group"])

    # This year - create measured value grouped by the key variables
    df_thisyear_weight = df_thisyear[["SchoolYear",
                                      "UpperTierLA",
                                      "IMD Quintile",
                                      "Ethnic Group",
                                      "NcmpSystemId"]].groupby(["SchoolYear",
                                                                "UpperTierLA",
                                                                "IMD Quintile",
                                                                "Ethnic Group"]).count().reset_index()

    df_thisyear_weight = df_thisyear_weight.rename(columns={"NcmpSystemId":
                                                            "measured_ThisYear"})

    # This year - create a link field
    df_thisyear_weight["Link_Field"] = (df_thisyear_weight["SchoolYear"] +
                                        df_thisyear_weight["UpperTierLA"] +
                                        " " +
                                        df_thisyear_weight["IMD Quintile"].astype(str) +
                                        df_thisyear_weight["Ethnic Group"])

    # This year - calculate school year total
    df_thisyear_weight["SchoolYearTotal"] = df_thisyear_weight.groupby(["SchoolYear"]).measured_ThisYear.transform("sum")

    # This year - calculate proportion for weighting
    df_thisyear_weight["proportion_ThisYear"] = (df_thisyear_weight["measured_ThisYear"] /
                                                 df_thisyear_weight["SchoolYearTotal"])

    # Base years - add current year measured value for each base year subgroup
    df_baseyears_weight = pd.merge(df_baseyears_weight,
                                   df_thisyear_weight[["Link_Field",
                                                       "measured_ThisYear"]],
                                   how="left",
                                   left_on=["Link_Field"],
                                   right_on=["Link_Field"])

    # Base years - update measured value to 0 when measured this year not available
    df_baseyears_weight["measuredWeighting"] = df_baseyears_weight["measured_BaseYear"]

    df_baseyears_weight.loc[(df_baseyears_weight["measured_ThisYear"].isnull()) |
                            (df_baseyears_weight["measured_ThisYear"] == 0),
                            "measuredWeighting"] = 0

    # Base years - calculate school year total
    df_baseyears_weight["SchoolYearTotal"] = df_baseyears_weight.groupby(["SchoolYear"]).measuredWeighting.transform("sum")

    # Base years - calculate proportion for weighting
    df_baseyears_weight["proportion_BaseYear"] = (df_baseyears_weight["measuredWeighting"] /
                                                  df_baseyears_weight["SchoolYearTotal"])

    # This year - match for each subgroup in the current year, the calulated proportion from baseyear subgroup
    df_thisyear_weight = pd.merge(df_thisyear_weight,
                                  df_baseyears_weight[["Link_Field",
                                                      "proportion_BaseYear"]],
                                  how="left",
                                  left_on=["Link_Field"],
                                  right_on=["Link_Field"])

    # This year - where subgroup not found in base years, replace proportion with 0
    df_thisyear_weight["proportion_BaseYear"].fillna(0, inplace=True)

    # This year - calculate weighting value
    df_thisyear_weight["Weight"] = (df_thisyear_weight["proportion_BaseYear"] /
                                    df_thisyear_weight["proportion_ThisYear"])

    # Combine weighted and unweighted data
    print("table_weighting - combining weighted and unweighted data")

    # Create a link field
    df_thisyear["Link_Field"] = (df_thisyear["SchoolYear"] +
                                 df_thisyear["UpperTierLA"] +
                                 " " +
                                 df_thisyear["IMD Quintile"].astype(str) +
                                 df_thisyear["Ethnic Group"])

    df_thisyear = pd.merge(df_thisyear,
                           df_thisyear_weight[["Link_Field", "Weight"]],
                           how="left",
                           left_on=["Link_Field"],
                           right_on=["Link_Field"])

    # Extract comparison year data from base data
    df_compyear = df_baseyears.loc[df_baseyears["AcademicYear"] == compyear[3:10]].copy()

    # Add year ref for comparison year
    df_compyear["Year_ref"] = "CompYear"

    # Add weight equal to 1 to comparison data
    df_compyear["Weight"] = 1

    # Create weighting table output
    print("table_weighting - creating outputs")

    # Combine comparison year and this year data
    df = df_compyear.append([df_thisyear])

    # Add unweighted value of 1 for all rows
    df["Unweighted"] = 1

    # Create table outputs
    def pupil_keygroups(df, breakdowns, sumcol):
        measured = df[["SchoolYear",
                       sumcol[0],
                       "Year_ref"]].groupby(["SchoolYear",
                                             "Year_ref"])[sumcol[0]].agg(Total="sum",
                                                                         Count="count").reset_index()

        measured["SchoolYear"] = measured["SchoolYear"].apply(str)
        measured["Year_ref"] = measured["Year_ref"].apply(str)

        subgroup = df[breakdowns + sumcol].groupby([*breakdowns]).sum().reset_index()
        subgroup = subgroup.rename(columns={sumcol[0]: "Value"})
        subgroup["SchoolYear"] = subgroup["SchoolYear"].apply(str)
        subgroup["Year_ref"] = subgroup["Year_ref"].apply(str)

        subgroup = pd.merge(subgroup,
                            measured,
                            how="left",
                            left_on=["Year_ref",
                                     "SchoolYear"],
                            right_on=["Year_ref",
                                      "SchoolYear"])

        subgroup["Proportion"] = subgroup["Value"]/subgroup["Total"] * 100

        subgroup = pd.pivot_table(subgroup,
                                  values=["Total",
                                          "Proportion",
                                          "Value",
                                          "Count"],
                                  index=breakdowns[:-1],
                                  columns="Year_ref").reset_index()

        subgroup.columns = [s1 + str(s2) for (s1, s2) in subgroup.columns.tolist()]

        subgroup["PercPointChange"] = (subgroup["ProportionThisYear"] -
                                       subgroup["ProportionCompYear"])

        return subgroup

    # Create weighted output, excluding rows with weights >4
    df_trim = df.loc[df["Weight"] <= 4]

    breakdowns = ["SchoolYear", "BmiPopulationCategory", "Year_ref"]
    sumcol = ["Weight"]

    df_bmi_weighted = pupil_keygroups(df_trim, breakdowns, sumcol)
    df_bmi_weighted = df_bmi_weighted[["SchoolYear", "BmiPopulationCategory",
                                       "ProportionCompYear",
                                       "ProportionThisYear",
                                       "TotalCompYear", "TotalThisYear",
                                       "ValueCompYear", "ValueThisYear",
                                       "PercPointChange", "CountThisYear",
                                       "CountCompYear"]]

    # Create BMI unweighted
    sumcol = ["Unweighted"]

    df_bmi_unweighted = pupil_keygroups(df, breakdowns, sumcol)
    df_bmi_unweighted = df_bmi_unweighted[["SchoolYear", "BmiPopulationCategory",
                                           "ProportionCompYear",
                                           "ProportionThisYear",
                                           "TotalCompYear", "TotalThisYear",
                                           "ValueCompYear", "ValueThisYear",
                                           "PercPointChange", "CountThisYear",
                                           "CountCompYear"]]

    # Add pupil extract date to outputs
    for df in [df_bmi_weighted, df_bmi_unweighted]:
        df["PupilExtractDate"] = datetime.strptime(param.PUPILS_FILE[27:35],
                                                   "%d%m%Y").date()

    # Export to Excel
    export_excel_data(df_bmi_weighted, "Weighted", outputpath)
    export_excel_data(df_bmi_unweighted, "Unweighted", outputpath)
