# utils/video_capture.py
import cv2
from cap_from_youtube import cap_from_youtube
def setup_video_capture(video_url, start_time=5, resolution='720p'):
    """
    Set up video capture from YouTube URL

    Args:
    video_url (str): YouTube video URL
    start_time (int): Time to start video from (in seconds)
    resolution (str): Video resolution

    Returns:
    cv2.VideoCapture: Configured video capture object
    """
    cap = cap_from_youtube(video_url, resolution=resolution)

    # Skip to specific start time
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_time * fps))

    return cap