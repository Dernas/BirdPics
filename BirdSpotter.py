import pickle
import os.path
from datetime import date
from googleapiclient.http import MediaFileUpload
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
    picname = "a"
    # Save the pic, using pic_count to keep track
    # Increment counter with each pic, name includes count
    print("d")
    # Send it to the drive
    send_pic(picname)


def ir_checker():
    print("c")


def send_pic(picname):

    # Get the date for folder check
    day = date.today()
    foldername = "AutoBirdPics " + day.strftime("%d-%b-%Y")
    # Google login code taken from https://developers.google.com/drive/api/v3/quickstart/python?authuser=1
    SCOPES = ['https://www.googleapis.com/auth/drive']  # Needs to create folders/files, see if folder exists
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time
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
    print("{0}".format(foldername))
    service = build('drive', 'v3', credentials=creds)

    # Check for a folder matching current date
    results = service.files().list(
        q="name='{0}'".format(foldername),
        spaces="drive",
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        # If it doesn't exist, create it
        # Format - AutoBirdPics dd-mon-yyyy
        folder_metadata = {
            "name": foldername,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": ["15Xn3O4BaGPRjun25PWNGyAZIX6p8NLFz"]
            # The ID of the BirdPics folder. Must be in a list to work as a parent, for reasons known only to Google
        }
        folder = service.files().create(body=folder_metadata,
                                        fields="id").execute()
        folderid = folder.get("id")
    else:
        # If it exists, get the ID
        folderid = items[0].get("id")



    # Add pic to today's folder
    ourdir = os.getcwd()
    picname = ourdir + "\\TestBird.jpg"
    pic = MediaFileUpload(picname, mimetype="image/jpeg")
    pic_meta = {"name": 'TestBird',
                "parents": ["{0}".format(folderid)]}
    # Google likes IDs better than names, so use the ID of the folder we made
    drivepic = service.files().create(body=pic_meta,
                                      media_body=pic,
                                      fields="id").execute()


if __name__ == "__main__":
    main()
