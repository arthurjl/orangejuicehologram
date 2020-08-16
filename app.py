from flask import Flask, render_template, url_for, request, redirect

import os # For file saving
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # This is how you can pass in information for the jinja liquid syntax
    # return render_template('index.html', tasks=tasks)
    tasks = [{'name': 'get stuff done', 'detail': 'yes yes yes'}, {'name': 'get stuff don1e', 'detail': 'yes yes y2es'}, {'name': 'g3et stuff done', 'detail': 'yes 4yes yes'},]
    return render_template('index.html', tasks=tasks)

# Place to save our files to
# (Should put in config file later maybe)
app.config["FILE_UPLOADS"] = "./static/uploads"
# Change later
app.config["ALLOWED_FILE_UPLOAD_EXTENSIONS"] = ["PNG", "JPG", "PDF", "JPEG", "MP4"]
app.config["MAX_FILESIZE"] = 5 * 1024 * 1024

@app.route('/upload', methods=['POST', 'GET'])
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

            video.save(os.path.join(app.config["FILE_UPLOADS"], filename))
            print(video)
            return redirect(request.url)

    # Else, GET request
    tasks = [{'name': 'get stuff done', 'detail': 'yes yes yes'}, {'name': 'get stuff don1e', 'detail': 'yes yes y2es'}, {'name': 'g3et stuff done', 'detail': 'yes 4yes yes'},]
    return render_template('upload.html', tasks=tasks)


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
    return int(filesize) < app.config["MAX_FILESIZE"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
