Warning - this repository is a snapshot of a repository internal to NHS Digital. This means that links to videos and some URLs may not work.***

***Repository owner: Analytical Services: Population Health, Clinical Audit and Specialist Care***

***Email: ncmp@nhs.net***

***To contact us raise an issue on Github or via email and we will respond promptly.***

# Getting Started

## Clone repository
To clone respositary, please see our [community of practice page](https://github.com/NHSDigital/rap-community-of-practice/blob/main/development-approach/02_using-git-collaboratively.md).

## Set up environment
There are two options to set up the python enviroment:
1. Pip using `requirements.txt`.
2. Conda using `environment.yml`.

Users would need to delete as appropriate which set they do not need. For details, please see our [virtual environments in the community of practice page](https://github.com/NHSDigital/rap-community-of-practice/blob/main/python/virtual-environments.md).


To set up the NCMP_INYEAR package enter the commands below (run one line at a time) in Anaconda Prompt (terminal on Mac/Linux):
```
pip install --user -r requirements.txt
```

or if using conda environments:
```
conda env create -f environment.yml
```

# National Child Measurement Programme (NCMP) background

The National Child Measurement Programme (NCMP) is a key element of the
Government’s approach to tackling child obesity by annually measuring the
height and weight of children in Reception (aged 4–5 years) and 
Year 6 (aged 10–11 years) in mainstream state-maintained schools in England. 

Local Authorities (LAs) in England measure children during the school year
with the programme running between September and August each year to coincide
with the academic year.

The data used in this project is provisional and based on extracts from the
NCMP system at a particular point in time within the submission period.

This project produces the required data tables for the provisional publication.


# Directory structure:
```
national-child-measurement-programme-rap
│
│__init__.py
│.gitignore                                 - Used to prevent files from being committed to this repo
│environment.yml                            - Used to install the conda environment
│LICENSE
│README.md
│requirements.txt                           - Used to install the python dependencies
│setup.py                                   - Used to install this pipeline as a package
│
├───ncmp_inyear_code                        - This is the main code directory for this project
│   │   create_publication_inyear.py        - This script runs the entire publication
│   │   parameters_inyear.py                - Contains parameters that define the how the publication will run
│   │   __init__.py                       
│   │   
│   ├───sql_code                            - This folder contains all the SQL queries used in the import data stage
│   │   │   query_ethnicity_ref.sql         - Defines the SQL query to import ethnicity reference data from corporate reference data
│   │   │   query_la_compyear.sql           - Defines the SQL query to import comparison year LA data from the NCMP table
│   │   │   query_la_e07_ref.sql            - Defines the SQL query to import LA reference data for E07 codes from corporate reference data
│   │   │   query_lsoa_ref.sql              - Defines the SQL query to import LSOA reference data from corporate reference data
│   │   │   query_pupils_baseyears.sql      - Defines the SQL query to import pupil data for base years for weighting outputs from NCMP table
│   │   │   query_pupils_compyear.sql       - Defines the SQL query to import pupil data for comparison year from NCMP table
│   │
│   ├───utilities                           - This module contains all the main modules used to create the publication
│   │   │   data_connections.py             - Defines the df_from_sql function, used when importing SQL data
│   │   │   export_inyear.py                - Defines the export_excel_data function, used when exporting table outputs to Excel
│   │   │   import_inyeardata.py            - Contains functions for reading in the required data from .csv files and SQL tables
│   │   │   table_bmi_prev.py               - Creates and exports to Excel the data required to populate the BMI prevalence tables
│   │   │   table_dqla.py                   - Creates and exports to Excel the data required to populate the LA data quality tables
│   │   │   table_ethnicity_imd.py          - Creates and exports to Excel the data required to populate the ethnicity and IMD tables
│   │   │   table_school_cohort.py          - Creates and exports to Excel the data required to populate the school cohort table
│   │   │   table_weighting.py              - Creates and exports to Excel the data required to populate the weighting table
│   │   │   __init__.py

```


# Running the publication process

There are two main files that users running the process will need to interact with:

- [parameters_inyear.py](ncmp_inyear_code/parameters_inyear.py)

- [create_publication_inyear.py](ncmp_inyear_code/create_publication_inyear.py)

Before processing a new set of extracts, the parameters_inyear.py file will
need to be reviewed and values updated as required.

This file specifies the input and output filepaths, the year filters,
LA exclusions/updates, etc., and also allows the user to control which
table outputs are generated when the process is run. 

The publication process is run using create_publication_inyear.py. 
This script imports and runs all the required functions for the table
outputs specified in the parameters file.

# Link to the publication
https://digital.nhs.uk/data-and-information/publications/statistical/national-child-measurement-programme/england-provisional-2021-22-school-year-outputs

# License
The NCMP InYear publication codebase is released under the MIT License.

Copyright © 2022, Health and Social Care Information Centre. The Health and Social Care Information Centre is a non-departmental body created by statute, also known as NHS Digital.
________________________________________
You may re-use this document/publication (not including logos) free of charge in any format or medium, under the terms of the Open Government Licence v3.0.
Information Policy Team, The National Archives, Kew, Richmond, Surrey, TW9 4DU;
email: psi@nationalarchives.gsi.gov.uk

