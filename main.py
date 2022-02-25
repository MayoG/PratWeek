from flask import Flask, render_template, redirect, url_for, request
from edit_video_utils import edit_video
from threading import Timer
import os

app = Flask(__name__, static_folder='static')


@app.route('/video')
def vid_page():
    vid_name = request.args["vid_name"]
    Timer(500, os.remove, args=(os.path.join("static", vid_name), )).start()
    return render_template('done_video.html', vid_name=vid_name)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        vid_path = os.path.join("static", uploaded_file.filename)
        edited_vid_path = os.path.join("static", f"edited_{uploaded_file.filename}")
        uploaded_file.save(vid_path)

        edit_video(video_path=vid_path,
                   color=tuple(map(int, request.form["topic"].split(', '))),
                   new_path=edited_vid_path,
                   delete_source=True)

        return redirect(url_for('vid_page', vid_name=f"edited_{uploaded_file.filename}"))


if __name__ == '__main__':
    app.run()