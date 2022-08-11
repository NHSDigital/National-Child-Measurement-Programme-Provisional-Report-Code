# Set the parameters for the project
import pathlib

"""FILEPATH PARAMETERS"""
# Sets the file paths for the project
BASE_DIR = pathlib.Path(r"projectfilepath")
INPUT_DIR = BASE_DIR / "Inputs"
INPUT_PUP_DIR = INPUT_DIR / "PupilData"
INPUT_REF_DIR = INPUT_DIR / "RefData"
INPUT_LADQ_DIR = INPUT_DIR / "LADQData"
OUTPUT_DIR = BASE_DIR / "Outputs"
OUTPUT_DIR_IY = OUTPUT_DIR / "In year analysis"

# Sets the path of the current LA file to be imported for LA DQ production (with extension)
LA_IY_FILE = "DataQualityAndProgressInformation.csv"
LA_IY_DATA_PATH = INPUT_LADQ_DIR / LA_IY_FILE

# Sets the path of the LA lookups file for LA DQ production (with extension)
LA_IY_LOOKUP_FILE = "LA_lookups_DQOutput.csv"
LA_IY_LOOKUP_PATH = INPUT_REF_DIR / LA_IY_LOOKUP_FILE

# Sets the path of the current enhanced pupil file to be imported for table production (with extension)
PUPILS_FILE = "IC_Enhanced_Pupils_2021_22.csv"
PUPILS_DATA_PATH = INPUT_PUP_DIR / PUPILS_FILE

# Set the path of the weighting ethnicity lookups file for In Year process
ETHNIC_GROUP = "Weighting_Ethnic_Grouping.csv"
ETHNIC_GROUP_PATH = INPUT_REF_DIR / ETHNIC_GROUP

# Set the path of the weighting imd lookups file for In Year process
IMD_QUINTILE = "IMD_Quintile_lookups.csv"
IMD_QUINTILE_PATH = INPUT_REF_DIR / IMD_QUINTILE

# Sets the filepath for the output file
IY_OUTPUT_FILE = "ncmp_inyear_source.xlsx"
IY_OUTPUT_PATH = OUTPUT_DIR_IY / IY_OUTPUT_FILE


"""PROCESS PARAMETERS"""
# Sets this year for process
IY_THISYEAR = "2021/22"

# Sets comparison year for process - used in SQL queries of NCMP table
IY_COMPYEAR = "= '2018/19'"

# Sets base years for weighting process - used in SQL queries of NCMP table
IY_BASEYEARS = "in ('2016/17', '2017/18','2018/19')"

# Sets LA(s) to exclude from comparison year dataset for LA DQ production
LA_IY_COMPEXCLUDE = ["809"]  # 809: Dorset, LA reconfigured and so 1819 data not comparable

# Dictionary of school URNs and LA code to assign to each URN for weighting process
# e.g. {148715: "E10000024"}
# Needed when a school URN doesn't have a school LSOA assigned in the pupil data file
URN_UPDATE_WEIGHTING_LA = {148715: "E10000024"}

# Sets which tables should be run as part of the create_publication process (True or False)
# Can be used to run individual outputs if needed
TABLE_BMI_PREV = True  # Tables 1 and 2
TABLE_DQLA = True # Tables A1 to A3
TABLE_ETH_IMD = True  # Tables B and C
TABLE_SCH_COHORT = True  # Table D
TABLE_WEIGHTING = True # Table E
