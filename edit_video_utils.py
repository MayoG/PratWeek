import dill as pickle
from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.segmenting import findObjects
import os
import numpy

colors_to_pickle = {
    (102, 153, 255): "LightBlue1.pkl",
    (218, 112, 214): "orchid.pkl",
    (255, 0, 0): "red.pkl",
    (211, 211, 211): "LightGray.pkl",
    (0, 0, 255): "CadetBlue.pkl",
}

colors_to_name = {
    (102, 153, 255): "LightBlue1",
    (218, 112, 214): "orchid",
    (255, 0, 0): "red",
    (211, 211, 211): "LightGray",
    (0, 0, 255): "CadetBlue",
}


def load_text(color, texts_path, screensize):
    # with open(os.path.join(texts_path, colors_to_pickle[color]), 'rb') as handle:
    #     b = pickle.load(handle)
    # return b

    # helper function
    with open(os.path.join(texts_path, colors_to_pickle[color]), 'rb') as handle:
        letters = pickle.load(handle)

    rotMatrix = lambda a: numpy.array([[numpy.cos(a), numpy.sin(a)],
                                       [-numpy.sin(a), numpy.cos(a)]])

    def cascade(screenpos, i, nletters):
        import numpy
        i = nletters - i
        v = numpy.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(numpy.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * 400 * d(t - 0.15 * i)

    def vortexout(screenpos, i, nletters):
        i = nletters - i
        d = lambda t: max(0, t)  # damping
        a = - numpy.pi / 2  # angle of the movement
        v = rotMatrix(a).dot([-1, 0])
        # if i % 2: v[1] = -v[1]
        return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)

    def moveLetters(letters, funcpos):
        return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
                for i, letter in enumerate(letters)]

    clips = [CompositeVideoClip(moveLetters(letters, funcpos), size=screensize).subclip(0, 5)
             for funcpos in [cascade, vortexout]]

    # clips = [CompositeVideoClip(moveLetters(letters, funcpos)).subclip(0, 5)
    #          for funcpos in [cascade, vortexout]]

    # WE CONCATENATE EVERYTHING AND WRITE TO A FILE

    final_clip = concatenate_videoclips(clips, method="compose")
    return final_clip


def edit_video(video_path, background_music, texts_path, color, new_path=None, delete_source=False):
    if not new_path:
        new_path = video_path
        delete_source = False

    with VideoFileClip(video_path) as my_clip:
        my_clip = my_clip.margin(mar=10, color=color)
        with AudioFileClip(background_music) as audio_background:
            audio_background = audio_background.set_end(my_clip.duration - 0.5)
            final_audio = CompositeAudioClip([my_clip.audio, audio_background])
            my_clip = my_clip.set_audio(final_audio)
            text_clip = load_text(color, texts_path, screensize=my_clip.size)
            # text_clip = create_intro_text(my_clip.size, color, texts_path)
            my_clip = CompositeVideoClip([my_clip, text_clip.set_pos('right')], size=my_clip.size)
            my_clip.write_videofile(new_path, codec="libx264", threads=4, logger=None)

    if delete_source:
        os.remove(video_path)


def create_intro_text(screensize, color, file_name):
    import numpy
    text = 'בה"ד קוד'.encode('utf-8')
    txtClip = TextClip(text, color=colors_to_name.get(color, "black"), font="Guttman-Aharoni-Bold",
                       kerning=10, fontsize=100)
    cvc = CompositeVideoClip([txtClip.set_position('right')])
    # cvc = CompositeVideoClip([txtClip.set_pos(('center', 'top'))], size=screensize)
    # cvc = CompositeVideoClip([txtClip])

    letters = findObjects(cvc, rem_thr=100)
    with open(file_name, "wb") as file:
        pickle.dump(letters, file)

    # # helper function
    # rotMatrix = lambda a: numpy.array([[numpy.cos(a), numpy.sin(a)],
    #                                 [-numpy.sin(a), numpy.cos(a)]])
    #
    # def cascade(screenpos, i, nletters):
    #     import numpy
    #     i = nletters - i
    #     v = numpy.array([0, -1])
    #     d = lambda t: 1 if t < 0 else abs(numpy.sinc(t) / (1 + t ** 4))
    #     return lambda t: screenpos + v * 400 * d(t - 0.15 * i)
    #
    # def vortexout(screenpos, i, nletters):
    #     i = nletters - i
    #     d = lambda t: max(0, t)  # damping
    #     a = - numpy.pi / 2  # angle of the movement
    #     v = rotMatrix(a).dot([-1, 0])
    #     # if i % 2: v[1] = -v[1]
    #     return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(v)
    #
    # def moveLetters(letters, funcpos):
    #     return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
    #             for i, letter in enumerate(letters)]
    #
    # # clips = [CompositeVideoClip(moveLetters(letters, funcpos), size=screensize).subclip(0, 5)
    # #          for funcpos in [cascade, vortexout]]
    #
    # clips = [CompositeVideoClip(moveLetters(letters, funcpos)).subclip(0, 5)
    #          for funcpos in [cascade, vortexout]]
    #
    # # WE CONCATENATE EVERYTHING AND WRITE TO A FILE
    #
    # final_clip = concatenate_videoclips(clips)
    # with open(file_name, "wb") as file:
    #     pickle.dump(final_clip, file)
    # return final_clip


if __name__ == '__main__':
    # edit_video(r'example_video.mp4',
    #            'utils/music/music_lower.mp3', texts_path='texts/', color=(255, 0, 0), new_path="test123.mp4")

    # create_intro_text((848, 480), (102, 153, 255), "texts/LightBlue1.pkl")
    # create_intro_text((848, 480), (218, 112, 214), "texts/orchid.pkl")
    # create_intro_text((848, 480), (255, 0, 0), "texts/red.pkl")
    # create_intro_text((848, 480), (211, 211, 211), "texts/LightGray.pkl")
    # create_intro_text((848, 480), (0, 0, 255), "texts/CadetBlue.pkl")

    edit_video(r'example_video.mp4',
               'utils/music/music_lower.mp3', texts_path='letters/', color=(255, 0, 0), new_path="test123.mp4")

    # create_intro_text((848, 480), (102, 153, 255), "letters/LightBlue1.pkl")
    # create_intro_text((848, 480), (218, 112, 214), "letters/orchid.pkl")
    # create_intro_text((848, 480), (255, 0, 0), "letters/red.pkl")
    # create_intro_text((848, 480), (211, 211, 211), "letters/LightGray.pkl")
    # create_intro_text((848, 480), (0, 0, 255), "letters/CadetBlue.pkl")
