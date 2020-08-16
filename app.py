from flask import Flask, render_template, url_for, request, redirect

import os # For file saving
from werkzeug.utils import secure_filename

from google_cloud import upload_blob

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
# Change later
app.config["ALLOWED_FILE_UPLOAD_EXTENSIONS"] = ["PNG", "JPG", "PDF", "JPEG", "MP4"]
app.config["MAX_FILESIZE"] = 5 * 1024 * 1024

# @app.route('/upload', methods=['POST', 'GET'])
# def upload():
#     if request.method == "POST":
#         if request.files:
#             video = request.files["video"]  # Matches 'name' attribute
#             if not is_filesize_allowed(request.cookies.get('filesize')):
#                 print(f"filesize exceeds limit of {app.config['MAX_FILESIZE']}")
#                 return redirect(request.url)
#             elif not is_filename_safe(video.filename):
#                 print("filename is not safe / allowed")
#                 return redirect(request.url)
#             filename = secure_filename(video.filename)
#             upload_location = os.path.join(app.config["FILE_UPLOADS"], filename)
#             print(f"Uploading file to {upload_location}")
#             upload_blob(video, upload_location)
#             return redirect(request.url)

#     # Else, GET request
#     return render_template('demo.html')


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
        if request.files:
            video = request.files["video"]  # Matches 'name' attribute
            if not is_filesize_allowed(request.cookies.get('filesize')):
                print(f"filesize exceeds limit of {app.config['MAX_FILESIZE']}")
                return redirect(request.url)
            elif not is_filename_safe(video.filename):
                print("filename is not safe / allowed")
                return redirect(request.url)
            filename = secure_filename(video.filename)
            upload_location = os.path.join(app.config["FILE_UPLOADS"], filename)
            print(f"Uploading file to {upload_location}")
            upload_blob(video, upload_location)
            return redirect(request.url)

    # Else, GET request
    return render_template('demo.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
