from datetime import datetime
import xlwings as xw
import pandas as pd


def export_excel_data(df, sheet, file_path):
    """
    This function will export the specified dataframe to the Excel file
    indicated

    Parameters:
        df:
            the dataframe to be exported
        sheet:
            the Excel workbook sheet to export the df to
        file_path: 
            the full file path and name of the Excel file to export to

    Returns:
        None

    """
    print(f"export_inyear - exporting outputs to {sheet} sheet of output file")

    # Add run date/time to file before export
    df["RunDate"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    # Open Excel application
    app = xw.App(visible=True)

    # Open output Excel workbook
    wb = xw.books.open(file_path)

    # Select data sheet and overwrite with latest data in dataframe
    sht = wb.sheets[sheet]
    sht.select()
    sht.clear_contents()
    sht.range("A1").options(pd.DataFrame, index=False).value = df

    # Save and close workbook
    wb.save(file_path)
    wb.close()

    # Close Excel
    app.quit()

    outputfile = str(file_path).split("\\")[-1]

    print(f"export_inyear - {sheet} sheet updated with latest data in {outputfile}")
