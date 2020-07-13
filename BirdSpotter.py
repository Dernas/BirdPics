import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time


def main():
    # Check if IR sensor has picked up any birds. Needs a rest timer if bird is found - 30 sec?
    # Temp: Run on a timer, pic every 10 min
    pic_count = 0
    #while True:
    pic_count += 1
    take_pic(pic_count)
    # time.sleep(600)


def take_pic(pic_num):
    # Take the picture. Should call the send_pic function, maybe take more than 1 pic
    print("b")
    # Save the pic, using pic_count to keep track
    print("d")
    # Send it to the drive
    send_pic()


def ir_checker():
    print("c")


def send_pic():
    # Send the pic off to the cloud. Need to set up a google drive or something for it
    # Probably make a folder for each day, check if exists. Increment counter with each pic, name includes count
    # Delete pic after, so we don't fill up hard drive? Shouldn't matter much, just let it overwrite.
    # Max will be the number of pics taken in one session (day)

    # Google login code taken from https://developers.google.com/drive/api/v3/quickstart/python?authuser=1
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']  # Needs to create folders/files, see if folder exists

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    # and mimeType='application/vnd.google-apps.folder'
    # Call the Drive v3 API
    z = service.files()
    results = service.files().list(q="'My Drive' in parents",
                                   spaces="drive",
                                   fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    print("d")


if __name__ == "__main__":
    main()
