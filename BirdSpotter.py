import pickle
import os
import os.path
import time
import datetime
import RPi.GPIO as GPIO
from picamera import PiCamera
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def main():
    # Check if IR sensor has picked up any birds.
    # 1 min delay before taking any pics, allow Pi to boot
    time.sleep(60)
    pir_input = 29
    start_pir(pir_input)
    current_day = datetime.date.today()
    start_time = datetime.time(5, 0, 0)
    end_time = datetime.time(21, 0, 0)
    pic_count = check_date()
    while True:
        current_time = datetime.datetime.now().time()
        if start_time < current_time < end_time:
            # Assumed no birds between 21:00 and 5:00
            if GPIO.input(pir_input):
                camera = PiCamera()
                camera.vflip = True
                camera.hflip = True
                take_pic(pic_count, camera)
                camera.close()
                pic_count += 1
                with open("Count.txt", "w+") as f:
                    f.write("%d" % pic_count)
                time.sleep(60)
            if datetime.date.today() != current_day:
                pic_count = check_date()
                current_day = datetime.date.today()


def check_date():
    # Check to see if it's a new day
    with open("Date.txt") as f:
        olddate = f.readline()
    date = datetime.date.today().strftime("%d-%b-%Y")
    if olddate == date:
        # If the day hasn't changed, we had a reboot or auto-check and should pick up the count where we left off
        with open("Count.txt") as g:
            pic_count = int(g.readline())
    else:
        # If it has, we set pic_count to 1 and update the date + saved count
        with open("Date.txt", "w") as f:
            f.write(date)
        with open("Count.txt", "r+") as g:
            g.write("1")
        pic_count = 1
    return pic_count


def take_pic(pic_num, camera):
    # Take the picture.
    camera.start_preview()
    # set the dir
    ourdir = "/home/pi/Birds/BirdPics/"
    picname = ourdir + "AutoPicture " + str(pic_num) + ".jpg"
    # Save the pic, using pic_num to keep track
    time.sleep(2)
    # Camera needs 2 seconds to adjust
    camera.capture(picname)
    camera.stop_preview()
    # Send it to the drive
    try:
        send_pic(picname, ourdir)
        send_offlines(ourdir)
        # If we got to this function, we have a connection again
    except:
        # This should be a more precise error, really just looking for if there's no connection. File is still saved
        # locally, and will be sent once connection is back
        # Rename the file to indicate it was saved offline
        os.rename(r"%s" % picname, r"OfflinePic " + datetime.datetime.now().strftime("%H:%M %d-%b-%Y") + ".jpg")
        pass


def start_pir(pir_input):
    # Pi pinout from https://learn.adafruit.com/assets/73285
    # Base code from https://www.electronicwings.com/raspberry-pi/pir-motion-sensor-interfacing-with-raspberry-pi
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pir_input, GPIO.IN)



def login(ourdir):
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
    service = build('drive', 'v3', credentials=creds)
    return service


def send_offlines(ourdir):
    # Send any pictures that were taken while offline to the drive
    service = login(ourdir)
    # check files in dir:
    for file in os.listdir(ourdir):
        if "Offline" in file:
            picturename = file.split(".")[0]
            # Get a nice name for the picture
            pic = MediaFileUpload(ourdir + "/" + file, mimetype="image/jpeg")
            pic_meta = {"name": picturename,
                        "parents": ["15Xn3O4BaGPRjun25PWNGyAZIX6p8NLFz"]}
            # Dump it into the main folder, let user use timestamps to sort
            service.files().create(body=pic_meta,
                                   media_body=pic,
                                   fields="id").execute()
            os.remove(file)


def send_pic(picname, ourdir):
    # Get the date for folder check
    day = datetime.date.today()
    foldername = "AutoBirdPics " + day.strftime("%d-%b-%Y")
    service = login(ourdir)
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
