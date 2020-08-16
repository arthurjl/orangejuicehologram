from flask import Flask, render_template, url_for, request, redirect

import os, shutil # For file saving and deleting
from werkzeug.utils import secure_filename

import backend.google_cloud as gc

from backend.video_converter import convertVideo
# import backend.background_remover as bgr

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
app.config["ALLOWED_FILE_UPLOAD_EXTENSIONS"] = ["MP4"]
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
            gc.upload_blob(video, upload_location)

            # Wait for download to exist and then save and then move on
            # download_location = os.path.join(app.config["FILE_TEMP_SAVE"], filename)
            # print(f'trying to download to {download_location}')
            # str_error = None
            # for x in range(0, 4):  # try 4 times
            #     try:
            #         print(f'trying to download to {download_location}, iteration {x}')
            #         str_error = None
            #         download_blob(upload_location, download_location)
            #     except Exception as ex:
            #         print(ex)
            #         str_error = ex

            #     if str_error:
            #         sleep(2 ** x)  # wait for 2 seconds before trying to fetch the data again
            #     else:
            #         break

            # if not os.path.isfile(download_location):
            #     print ("File was not downloaded successfully!")
            #     return redirect(request.url)

            # Get the signed url to pass to removed background
            file_url = gc.generate_signed_url(upload_location)
            print('converted:' + file_url)

            # Not using the removedBackground for now
            # removedBackround = bgr.BackgroundRemover(cv2.VideoCapture(download_location)).process()
            # removedBackround = download_location
            converted_vid_name = convertVideo(file_url, 50)
            print('converted:' + converted_vid_name)
            convert_vid_url = gc.generate_signed_url(converted_vid_name)
            print('converted:' + convert_vid_url)

            # final_loc = os.path.join(app.config["FILE_TEMP_SAVE"], converted_vid)
            # shutil.move(converted_vid, final_loc)
            return render_template('demo.html', video_loc=convert_vid_url)

    # Else, GET request
    # return render_template('demo.html', video_loc="https://orangejuicehologram.appspot.com.storage.googleapis.com/uploads/video-1597551723_1.mp4?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=fileuploader%40orangejuicehologram.iam.gserviceaccount.com%2F20200816%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20200816T102944Z&X-Goog-Expires=604800&X-Goog-SignedHeaders=host&x-goog-signature=912ea78acb98ab4e1199b9e0f41c80158f37fa26cf4645a05c87776607c609503c0516959e0375f90c1b63a703b2a687d81fba9c95804abaddcc439411ad5b5036672583cd4fa02a1126303d04e37d974ce3b321eef95a1128d2ed0f8617984dddae824c13df9fc5bd8f03e29fe720521712e5e6740bd796431134d6ecce2502a029e4e9aa0055323bdd4309fd2d649a222a0e4f4d7638dee31f52cc8724c9fde2192155c1d1565ec0f2a8e21167af86b69201b93bb1fff6331af4f02fef2bf4f06d6e62255e2d938976ac3ad2954e76c1e42ba026a7b15c94dedd1552c028a574b48f43555679b38690de84cf6dc4f38e820910623fc237b3cc79768aaa67d6")
    return render_template('demo.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    # print(gc.generate_signed_url('uploads/video-1597551723_1.mp4'))