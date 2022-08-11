import pandas as pd

import ncmp_inyear_code.parameters_inyear as param
import ncmp_inyear_code.utilities.import_inyeardata as import_inyeardata
from ncmp_inyear_code.utilities.table_bmi_prev import create_table_bmi_prev
from ncmp_inyear_code.utilities.table_dqla import create_table_dqla
from ncmp_inyear_code.utilities.table_ethnicity_imd import create_table_ethnicity_imd
from ncmp_inyear_code.utilities.table_school_cohort import create_table_school_cohort
from ncmp_inyear_code.utilities.table_weighting import create_table_weighting

# Import data based on table processes selected to run in parameters file
if param.TABLE_BMI_PREV | param.TABLE_ETH_IMD | param.TABLE_SCH_COHORT | param.TABLE_WEIGHTING:

    # Import pupil data (NCMP schools only with BMI measurements)
    df_pupils_import = import_inyeardata.import_pupils_data(param.PUPILS_DATA_PATH)

if param.TABLE_BMI_PREV | param.TABLE_ETH_IMD | param.TABLE_SCH_COHORT:

    # Import comparison year data from NCMP SQL table
    df_pupils_compyear = import_inyeardata.import_pupils_compyear(param.IY_COMPYEAR)

if param.TABLE_ETH_IMD | param.TABLE_WEIGHTING:

    # Import ethnicity reference data
    df_ethnicity_ref = import_inyeardata.import_ethnicity_ref()

if param.TABLE_WEIGHTING:

    # Import pupil data for base years
    df_pupils_baseyears = import_inyeardata.import_pupils_baseyears(param.IY_BASEYEARS)

    # Import OHID ethnicity and IMD reference data
    print("import_inyeardata - importing OHID ethnicity and IMD reference data")
    df_ethnicity_ref_ohid = pd.read_csv(param.ETHNIC_GROUP_PATH)
    df_imd_ref_ohid = pd.read_csv(param.IMD_QUINTILE_PATH)

    # Import LSOA reference data
    df_lsoa_ref = import_inyeardata.import_lsoa_ref()

    # Import LA reference data for E07 codes
    df_la_e07_ref = import_inyeardata.import_la_e07_ref()

if param.TABLE_DQLA:

    # Import LA DQ data
    df_la_import = import_inyeardata.import_LA_DQ_data(param.LA_IY_DATA_PATH)

    # Import comparison year data from NCMP SQL table
    df_la_compyear = import_inyeardata.import_LA_compyear(param.IY_COMPYEAR)

    # Import LA to reporting region lookups
    print("import_inyeardata - importing LA to reporting region lookups")
    df_la_lookups = pd.read_csv(param.LA_IY_LOOKUP_PATH)

# Create and export table outputs based on those selected to run in parameters file
if param.TABLE_BMI_PREV:
    create_table_bmi_prev(df_pupils_import, param.IY_OUTPUT_PATH)

if param.TABLE_DQLA:
    create_table_dqla(df_la_import, df_la_compyear, df_la_lookups,
                      param.LA_IY_COMPEXCLUDE, param.IY_OUTPUT_PATH)

if param.TABLE_ETH_IMD:
    create_table_ethnicity_imd(df_pupils_import, df_pupils_compyear,
                               df_ethnicity_ref, param.IY_THISYEAR,
                               param.IY_OUTPUT_PATH)

if param.TABLE_SCH_COHORT:
    create_table_school_cohort(df_pupils_import, df_pupils_compyear,
                               param.IY_THISYEAR, param.IY_OUTPUT_PATH)


if param.TABLE_WEIGHTING:
    create_table_weighting(df_pupils_import, df_pupils_baseyears,
                           df_ethnicity_ref, df_lsoa_ref, df_la_e07_ref,
                           df_ethnicity_ref_ohid, df_imd_ref_ohid,
                           param.IY_THISYEAR, param.IY_COMPYEAR,
                           param.IY_OUTPUT_PATH)
