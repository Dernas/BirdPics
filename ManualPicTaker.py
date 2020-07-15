import pickle
import os.path
import time
import sys
from datetime import date
from datetime import datetime
from picamera import PiCamera
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main():
    # Take a pic when requested by the user
    try:
        take_pic()
    except Exception as e:
        print(e)
        print("Picture failed! Camera in use or no internet connection")
        sys.exit(-1)
    sys.exit(0)


def take_pic():
    # Takes the picture.
    # set the dir
    currenttime = datetime.now()
    ourdir = "/home/pi/Birds/BirdPics/"
    picname = ourdir + "ManualPicture" + currenttime.strftime("%H-%M-%S") + ".jpg"
    camera = PiCamera()
    camera.vflip = True
    camera.hflip = True
    camera.start_preview()
    # Save the pic, using pic_num to keep track
    time.sleep(2)
    # Camera needs 2 seconds to adjust
    camera.capture(picname)
    camera.stop_preview()
    camera.close()
    # Send it to the drive
    send_pic(picname, ourdir)


def send_pic(picname, ourdir):
    # Get the date for folder check
    day = date.today()
    foldername = "AutoBirdPics " + day.strftime("%d-%b-%Y")
    # Google login code taken from https://developers.google.com/drive/api/v3/quickstart/python?authuser=1
    SCOPES = ['https://www.googleapis.com/auth/drive']  # Needs to create folders/files, see if folder exists
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time
    if os.path.exists(ourdir + 'token.pickle'):
        with open(ourdir + 'token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
               ourdir + 'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(ourdir + 'token.pickle', 'wb') as token:
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

    filename = picname.split("/")[-1]
    picturename = filename.split(".")[0]
    # Get a nice name for the picture

    # Add pic to today's folder
    pic = MediaFileUpload(picname, mimetype="image/jpeg")
    pic_meta = {"name": picturename,
                "parents": ["{0}".format(folderid)]}
    # Google likes IDs better than names, so use the ID of the folder we made
    service.files().create(body=pic_meta,
                           media_body=pic,
                           fields="id").execute()


if __name__ == "__main__":
    main()
