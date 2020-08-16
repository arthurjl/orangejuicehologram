from flask import Flask, render_template, url_for, request, redirect

import os, shutil # For file saving and deleting
from werkzeug.utils import secure_filename

import cv2

from google_cloud import upload_blob, download_blob

from backend.video_converter import convertVideo
import backend.background_remover as bgr

from time import sleep

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # This is how you can pass in information for the jinja liquid syntax
    # return render_template('index.html', tasks=tasks)
    tasks = [{'name': 'get stuff done', 'detail': 'yes yes yes'}, {'name': 'get stuff don1e', 'detail': 'yes yes y2es'}, {'name': 'g3et stuff done', 'detail': 'yes 4yes yes'},]
    return render_template('index.html', tasks=tasks)

# Place to save our files to
# (Should put in config file later maybe)
app.config["FILE_UPLOADS"] = "uploads/"
app.config["FILE_TEMP_SAVE"] = "static/temp/"
# Change later
app.config["ALLOWED_FILE_UPLOAD_EXTENSIONS"] = ["PNG", "JPG", "PDF", "JPEG", "MP4"]
app.config["MAX_FILESIZE"] = 5 * 1024 * 1024

def is_filename_safe(filename):
    if filename == "":
        print("File must have a filename")
        return False
    elif not "." in filename:
        print("File does not have extensions")
        return False

    ext = filename.rsplit(".", 1)[1]

    return ext.upper() in app.config["ALLOWED_FILE_UPLOAD_EXTENSIONS"]

def is_filesize_allowed(filesize):
    if not filesize:
        print('Cookies must be enabled to support upload (for our security purposes)')
        return False
    return int(filesize) < app.config["MAX_FILESIZE"]

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')

@app.route('/demo', methods=['POST', 'GET'])
def upload():
    if request.method == "POST":
        # TODO: delete files in temp first
        # for file_to_delete in os.listdir(app.config["FILE_TEMP_SAVE"]):
        #     file_path_to_delete = os.path.join(app.config["FILE_TEMP_SAVE"], file_to_delete)
        #     print(f'trying to yeet {file_path_to_delete}')
        #     try:
        #         if os.path.isfile(file_path_to_delete) or os.path.islink(file_path_to_delete):
        #             os.unlink(file_path_to_delete)
        #         elif os.path.isdir(file_path_to_delete):
        #             shutil.rmtree(file_path_to_delete)
        #     except Exception as e:
        #         print('Failed to delete %s. Reason: %s' % (file_path_to_delete, e))

        if request.files:
            video = request.files["video"]  # Matches 'name' attribute

            video.seek(0, os.SEEK_END)
            size = video.tell()
            video.seek(0, 0)
            if int(size) > app.config["MAX_FILESIZE"]:
                print(f"filesize exceeds limit of {app.config['MAX_FILESIZE']}")
                return redirect(request.url)
            elif not is_filename_safe(video.filename):
                print("filename is not safe / allowed")
                return redirect(request.url)
            filename = secure_filename(video.filename)
            upload_location = os.path.join(app.config["FILE_UPLOADS"], filename)

            print(f"Uploading file to {upload_location}")
            upload_blob(video, upload_location)

            # Wait for download to exist and then save and then move on
            download_location = os.path.join(app.config["FILE_TEMP_SAVE"], filename)
            print(f'trying to download to {download_location}')
            str_error = None
            for x in range(0, 4):  # try 4 times
                try:
                    print(f'trying to download to {download_location}, iteration {x}')
                    str_error = None
                    download_blob(upload_location, download_location)
                except Exception as ex:
                    print(ex)
                    str_error = ex

                if str_error:
                    sleep(2 ** x)  # wait for 2 seconds before trying to fetch the data again
                else:
                    break

            if not os.path.isfile(download_location):
                print ("File was not downloaded successfully!")
                return redirect(request.url)

            # Not using the removedBackground for now
            # removedBackround = bgr.BackgroundRemover(cv2.VideoCapture(download_location)).process()
            removedBackround = download_location
            converted_vid = convertVideo(removedBackround, 50)
            final_loc = converted_vid
            # final_loc = os.path.join(app.config["FILE_TEMP_SAVE"], converted_vid)
            # shutil.move(converted_vid, final_loc)
            return render_template('demo.html', video_loc=final_loc)

    # Else, GET request
    return render_template('demo.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
