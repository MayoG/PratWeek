import os

from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip


def edit_video(video_path, background_music, color, new_path=None, delete_source=False):
    print(video_path)
    if not new_path:
        new_path = video_path
        delete_source = False

    with VideoFileClip(video_path) as my_clip:
        my_clip = my_clip.margin(mar=10, color=color)
        with AudioFileClip(background_music) as audio_background:
            audio_background = audio_background.set_end(my_clip.duration - 0.5)
            final_audio = CompositeAudioClip([my_clip.audio, audio_background])
            my_clip = my_clip.set_audio(final_audio)
            my_clip.write_videofile(new_path, codec="libx264", threads=4, logger=None)

    if delete_source:
        os.remove(video_path)


if __name__ == '__main__':
    edit_video(r'C:\Users\user\Downloads\trim.04212816-F4B6-4241-B3A1-73133DD435A4.mov',
               'utils/music/music_lower.mp3', color=(255, 255, 0), new_path="test123.mp4")
