import cv2
from moviepy.editor import CompositeVideoClip, VideoFileClip, clips_array, vfx

# Converts video into three-dimensional projection format
def convertVideo(filepath, percentage):
    # TODO: Edit preset dimensions
    width = 2000

    # Resize original clip
    clip1 = VideoFileClip(filepath).resize(percentage / 100.0)
    clip_width = clip1.w
    clip_height = clip1.h

    # Generate other clips from original
    clip2 = clip1.rotate(90)
    clip3 = clip1.rotate(180)
    clip4 = clip1.rotate(270)

    # Retrieve clip of white border for placement of cone
    clip5 = ColorClip(size=(400, 400), color=(255, 255, 255))
    clip6 = ColorClip(size=(390, 390), color=(0, 0, 0))

    # Calculate clip positions
    clip1_pos = ((width / 2) - (clip_width / 2), 0)
    clip2_pos = (0, (width / 2) - (clip_width / 2))
    clip3_pos = ((width / 2) - (clip_width / 2), width - clip_height)
    clip4_pos = (width - clip_height, (width / 2) - (clip_width / 2))
    clip5_pos = ((width / 2) - 200, (width / 2) - 200)
    clip6_pos = ((width / 2) - 195, (width / 2) - 195)

    # Produce composition of clips
    final_clip = CompositeVideoClip([clip1.set_position(clip1_pos),
                                    clip2.set_position(clip2_pos),
                                    clip3.set_position(clip3_pos),
                                    clip4.set_position(clip4_pos)], size=(width, width))
    print(filepath)
    corrected_filepath = filepath[:filepath.find(".")] + ".mp4"
    print(corrected_filepath)
    # final_clip.write_videofile(corrected_filepath, codec='mpeg4')
    # final_clip.write_videofile(corrected_filepath)
    # return corrected_filepath
