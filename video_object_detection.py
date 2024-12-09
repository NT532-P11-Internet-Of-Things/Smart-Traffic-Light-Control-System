# main.py
from utils import TrafficMonitor

video = [
    'https://www.youtube.com/watch?v=SYJQZFVGh90', # 0
    'https://www.youtube.com/watch?v=CbB7p9rBZSc', # 1
    'https://www.youtube.com/watch?v=YU4Bbbp2oA4', # 2
    'https://www.youtube.com/watch?v=WlU4OvOnQTw', # 3
    'https://www.youtube.com/watch?v=AqpRdLYcXaY', # 4
    'https://www.youtube.com/watch?v=iwTNmVCaT4w', # 5
    'https://www.youtube.com/watch?v=VKj4CzFRIOU', # 6
    'https://www.youtube.com/watch?v=MD8LxvaE0OA', # 7
    'https://www.youtube.com/watch?v=yOosBwk_xNk', # 8 
    'https://www.youtube.com/watch?v=XdzXqbyKeQw', # 9  Ko có xe
    'https://www.youtube.com/watch?v=jYeAVWWrp9g', # 10
    'https://www.youtube.com/watch?v=QvVd9WyxHUA', # 11

    'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
    'https://youtu.be/Kc-jyoCHZq8',
    'https://youtu.be/SqxQRLcUvf4',
    'https://youtu.be/xQlMXaL8yZs'

    ]


def main():
    # Video URLs for 4 lanes
    video_urls = [
        video[3],
        video[4],
        video[5],
        video[14],
    ]

    # Path to YOLO model
    model_path = "models/yolov8m.onnx"
    firebase_credentials = "credential/smart-traffic-light-03-firebase-adminsdk-mzf6v-45aa726e71.json"

    # Create and run traffic monitor
    monitor = TrafficMonitor(video_urls, model_path, firebase_credentials)
    monitor.run()

if __name__ == "__main__":
    main()