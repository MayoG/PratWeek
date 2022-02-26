import os
import numpy as np
from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.segmenting import findObjects

colors = {
    (102, 153, 255): "LightBlue1",
    (218, 112, 214): "orchid",
    (255, 0, 0): "LightYellow",
    (211, 211, 211): "LightGray",
    (0, 0, 255): "CadetBlue",
}


def edit_video(video_path, background_music, color, new_path=None, delete_source=False):
    if not new_path:
        new_path = video_path
        delete_source = False

    with VideoFileClip(video_path) as my_clip:
        my_clip = my_clip.margin(mar=10, color=color)
        with AudioFileClip(background_music) as audio_background:
            audio_background = audio_background.set_end(my_clip.duration - 0.5)
            final_audio = CompositeAudioClip([my_clip.audio, audio_background])
            my_clip = my_clip.set_audio(final_audio)
            text_clip = create_intro_text(screensize=my_clip.size, color=color)
            my_clip = CompositeVideoClip([my_clip, text_clip])
            my_clip.write_videofile(new_path, codec="libx264", threads=4, logger=None)

    if delete_source:
        os.remove(video_path)


def create_intro_text(screensize, color):
    text = 'בה"ד קוד'.encode('utf-8')
    txtClip = TextClip(text, color=colors.get(color, "black"), font="Guttman-Aharoni-Bold",
                       kerning=10, fontsize=100)
    cvc = CompositeVideoClip([txtClip.set_pos(('center', 'top'))],
                             size=screensize)

    # helper function
    rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)],
                                    [-np.sin(a), np.cos(a)]])

    def cascade(screenpos, i, nletters):
        i = nletters - i
        v = np.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * 400 * d(t - 0.15 * i)

    def vortexout(screenpos, i, nletters):
        i = nletters - i
        d = lambda t: max(0, t)  # damping
        a = - np.pi / 2  # angle of the movement
        v = rotMatrix(a).dot([-1, 0])
        # if i % 2: v[1] = -v[1]
        return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)

    letters = findObjects(cvc, rem_thr=100)

    def moveLetters(letters, funcpos):
        return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
                for i, letter in enumerate(letters)]

    clips = [CompositeVideoClip(moveLetters(letters, funcpos),
                                size=screensize).subclip(0, 5)
             for funcpos in [cascade, vortexout]]

    # WE CONCATENATE EVERYTHING AND WRITE TO A FILE

    final_clip = concatenate_videoclips(clips)
    return final_clip


if __name__ == '__main__':
    # edit_video(r'C:\Users\user\Downloads\trim.04212816-F4B6-4241-B3A1-73133DD435A4.mov',
    #            'utils/music/music_lower.mp3', color=(255, 255, 0), new_path="test123.mp4")
    edit_video(r'example_video.mp4',
               'utils/music/music_lower.mp3', color=(255, 0, 0), new_path="test123.mp4")
