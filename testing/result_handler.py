import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


# use creds to create a client to interact with the Google Drive API


# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
# sheet = client.open("Untitled form (Responses)").sheet1
def get_by_url(url):
    scope = ['https://spreadsheets.google.com/feeds']
    file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'testing/client_secret.json')
    creds = ServiceAccountCredentials.from_json_keyfile_name(file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(url).sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    result = {}
    for i in list_of_hashes:
        result[i['Email Address']] = i['Score'].split(' / ')[0]
    return result
