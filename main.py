from flask import Flask, render_template, redirect, url_for, request
from edit_video_utils import edit_video
import os

app = Flask(__name__, static_folder='static')
root_path = app.root_path


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        vid_path = os.path.join(root_path, "static", uploaded_file.filename)
        edited_vid_path = os.path.join(root_path, "static", f"edited_{uploaded_file.filename}")
        uploaded_file.save(vid_path)

        edit_video(video_path=vid_path,
                   background_music=os.path.join(root_path, 'utils', 'music', 'music_lower.mp3'),
                   color=tuple(map(int, request.form["topic"].split(', '))),
                   new_path=edited_vid_path,
                   delete_source=True)

        return redirect(url_for('static', filename=f"edited_{uploaded_file.filename}"))


if __name__ == '__main__':
    app.run()