import pickle
import os.path
import time
from datetime import date
from picamera import PiCamera
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main():
    # Check if IR sensor has picked up any birds.
    # Temp: Run on a timer, pic every 10 min
    # 1 min delay before taking any pics, allow Pi to boot
    time.sleep(60)
    pic_count = 0
    while True:
        camera = PiCamera()
        camera.vflip = True
        camera.hflip = True
        pic_count += 1
        take_pic(pic_count, camera)
        camera.close()
        time.sleep(600)


def take_pic(pic_num, camera):
    # Take the picture.
    camera.start_preview()
    # set the dir
    ourdir = "/home/pi/Birds/BirdPics/"
    picname = ourdir + "AutoPicture" + str(pic_num) + ".jpg"
    # Save the pic, using pic_num to keep track
    time.sleep(2)
    # Camera needs 2 seconds to adjust
    camera.capture(picname)
    camera.stop_preview()
    # Send it to the drive
    try:
        send_pic(picname, ourdir)
    except:
        # This should be a more precise error, really just looking for if there's no connection. File is still saved
        # locally, so can SCP and grab it if needed once connection is restored
        pass


def ir_checker():
    print("c")


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
    drivepic = service.files().create(body=pic_meta,
                                      media_body=pic,
                                      fields="id").execute()


if __name__ == "__main__":
    main()
