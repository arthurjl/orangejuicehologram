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

    # Calculate clip positions
    clip1_pos = ((width / 2) - (clip_width / 2), 0)
    clip2_pos = (0, (width / 2) - (clip_width / 2))
    clip3_pos = ((width / 2) - (clip_width / 2), width - clip_height) 
    clip4_pos = (width - clip_height, (width / 2) - (clip_width / 2))

    # Produce composition of clips
    final_clip = CompositeVideoClip([clip1.set_position(clip1_pos), 
                                    clip2.set_position(clip2_pos), 
                                    clip3.set_position(clip3_pos), 
                                    clip4.set_position(clip4_pos)], size=(width, width))
    final_clip.write_videofile(filepath.replace(".mp4", "_converted.mp4"))

convertVideo("lebron_test.mp4", 55)