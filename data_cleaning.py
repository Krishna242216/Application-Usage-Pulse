def sequ():
    import pandas as pd
    import gspread
    from gspread_dataframe import get_as_dataframe, set_with_dataframe
    from oauth2client.service_account import ServiceAccountCredentials

    # Define the scope and authenticate with your service account file
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('Credentials.json', scope)
    gc = gspread.authorize(credentials)

    # Open the Google Sheet by name or URL
    sheet = gc.open("Test_Postgres")  # Use the actual Google Sheet name or URL
    worksheet = sheet.worksheet('App_Actions')  # Access the worksheet by name

    # Fetch the data into a DataFrame
    data = get_as_dataframe(worksheet, evaluate_formulas=True, dtype=str)

    # Remove rows where the 'Date' column is null or empty
    data = data.dropna(subset=['client_timestamp']).reset_index(drop=True)  # Replace 'Date' with the actual column name
    data = data[data['client_timestamp'].str.strip() != '']  # Removes rows with empty strings in the 'Date' column

    def format_username(row):
        if pd.notna(row['username']):
            # If a username exists, return it
            return row['username']

        if pd.isna(row['username']) and pd.notna(row['email_id']):
            name_part = row['email_id'].split('@')[0]  # Get the part before '@'
            # Split by '.' and capitalize first letters
            names = name_part.split('.')
            formatted_name = ' '.join(name.capitalize() for name in names)
            return formatted_name

        return None  # Return None if both are NaN

    data['username'] = data.apply(format_username, axis=1)

    # Update email_id and username to "Not Performed" if email_id is null
    data.loc[pd.isna(data['email_id']), 'email_id'] = "Not Performed Actions"
    data.loc[pd.isna(data['username']), 'username'] = "Not Performed Actions"

    # Replace specific case
    data.loc[data['username'] == 'Shiva Raavi', 'username'] = 'Raavi S'

    # Clear the existing worksheet content before writing new data
    num_rows = worksheet.row_count  # Total number of rows in the worksheet
    range_to_clear = f"A1:M{num_rows}"  # Specify the range (up to column M)
    worksheet.batch_clear([range_to_clear])

    # Limit the DataFrame to columns A to M
    data = data.iloc[:, :13]  # Keep only the first 13 columns (A to M)

    # Write DataFrame to Google Sheet
    set_with_dataframe(worksheet, data)
    print(f"Data successfully updated in the 'App_Actions' tab in the same Google Sheet.")
