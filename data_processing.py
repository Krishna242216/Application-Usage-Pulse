def seqtoo():
    import pandas as pd
    import gspread
    from gspread_dataframe import set_with_dataframe
    from oauth2client.service_account import ServiceAccountCredentials

    # Define the scope and authenticate with your service account file
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('Credentials.json', scope)
    gc = gspread.authorize(credentials)

    # Open the Google Sheet by URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1I5Vyi5BM1goO72SD1KNjg6FxFC1rZKSQ5B6Wqg7Pvc8/edit"
    sheet = gc.open_by_url(spreadsheet_url)

    # Access the specific tab (Updated_data) in the sheet
    worksheet = sheet.worksheet("App_Actions")  # Adjust if your tab name is different

    # Fetch the data into a DataFrame
    data = pd.DataFrame(worksheet.get_all_records())

    # Ensure the client_timestamp column is a datetime type
    data['client_timestamp'] = pd.to_datetime(data['client_timestamp'], errors='coerce')

    # Check if there are any NaT values and handle them if needed
    if data['client_timestamp'].isna().any():
        print("Warning: Some values in 'client_timestamp' could not be converted and are now NaT.")

    # Sort by username, App Name, and client_timestamp
    data = data.sort_values(by=['username', 'App Name', 'client_timestamp'])

    # Calculate time differences per username and App Name in seconds
    data['time_diff'] = data.groupby(['username', 'App Name'])['client_timestamp'].diff().dt.total_seconds()

    # Replace NaN values in time_diff with 0 for the first entry of each user and app
    data['time_diff'] = data['time_diff'].fillna(0)

    # Detect gaps greater than or equal to 30 minutes (1800 seconds)
    # Mark these gaps as 'session break'
    data['session_break'] = data['time_diff'] >= 1800

    # Initialize session_id, start from 1 for the first session within each user and app
    data['session_id'] = data.groupby(['username', 'App Name'])['session_break'].cumsum() + 1

    # Now, for each session, calculate the total time, ignoring the 30-minute gaps
    def calculate_session_time(group):
        # Exclude the 30-minute gaps
        group['valid_time_diff'] = group['time_diff'].where(group['time_diff'] < 1800, 0)
        # Sum the valid time differences within the session
        group['session_time'] = group['valid_time_diff'].cumsum()
        return group

    data = data.groupby(['username', 'App Name', 'session_id']).apply(calculate_session_time)

    # Convert session_time to a readable format (hh:mm:ss)
    def convert_seconds_to_hms(seconds):
        return str(pd.to_timedelta(seconds, unit='s')).split()[2]

    data['session_time_hms'] = data['session_time'].apply(convert_seconds_to_hms)

    # Drop unnecessary columns
    data = data.drop(columns=['valid_time_diff', 'session_break'])

    # Create or access the tab called 'time_updated'
    new_sheet_name = "time_updated"  # Change the name of the new tab if needed

    try:
        # Try to access the existing worksheet
        new_worksheet = sheet.worksheet(new_sheet_name)
        # Clear the existing worksheet content up to column U
        num_rows = new_worksheet.row_count
        range_to_clear = f"A1:U{num_rows}"
        new_worksheet.batch_clear([range_to_clear])
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet does not exist, create a new one
        new_worksheet = sheet.add_worksheet(title=new_sheet_name, rows=str(data.shape[0] + 1), cols=str(data.shape[1]))

    # Limit the DataFrame to columns A to U if necessary
    data = data.iloc[:, :21]  # Adjust column count if needed

    # Write the updated data to the worksheet
    set_with_dataframe(new_worksheet, data)

    # Print success message
    print(f"Data successfully saved to the '{new_sheet_name}' tab in the same Google Sheet.")
