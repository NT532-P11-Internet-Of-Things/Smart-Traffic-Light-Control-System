# main.py
from utils import TrafficMonitor

video = [
    'https://www.youtube.com/watch?v=SYJQZFVGh90', # 0
    'https://www.youtube.com/watch?v=CbB7p9rBZSc', # 1
    'https://www.youtube.com/watch?v=YU4Bbbp2oA4', # 2
    'https://www.youtube.com/watch?v=WlU4OvOnQTw', # 3 10 xe
    'https://www.youtube.com/watch?v=AqpRdLYcXaY', # 4 9 xe nhma đếm ko trong làn nữa
    'https://www.youtube.com/watch?v=iwTNmVCaT4w', # 5 ko chay dc
    'https://www.youtube.com/watch?v=VKj4CzFRIOU', # 6 ko chay dc
    'https://www.youtube.com/watch?v=MD8LxvaE0OA', # 7 toi ko chay dc
    'https://www.youtube.com/watch?v=yOosBwk_xNk', # 8 toi 2 xe
    'https://www.youtube.com/watch?v=XdzXqbyKeQw', # 9  Ko có xe nhma do ko dem dc
    'https://www.youtube.com/watch?v=jYeAVWWrp9g', # 10
    'https://www.youtube.com/watch?v=QvVd9WyxHUA', # 11

    'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
    'https://youtu.be/Kc-jyoCHZq8',
    'https://youtu.be/SqxQRLcUvf4',
    'https://youtu.be/xQlMXaL8yZs',

    'https://www.youtube.com/watch?v=NBWd_5AZ79E', # 16 ko sài đc
    'https://www.youtube.com/watch?v=7LrWGGJFEJo', # 17 12 xe có lúc 19
    'https://www.youtube.com/watch?v=CftLBPI1Ga4', # 18 15 xe  
    'https://www.youtube.com/watch?v=XgqTf1f-5Hw', # 19 nhanh quá đếm ko đc 

    ]


def main():
    # Video URLs for 4 lanes
    video_urls = [
        video[2],
        video[3],
        video[8],
        video[8],
    ]

    # Path to YOLO model
    model_path = "models/yolov8m.onnx"
    firebase_credentials = "credential/smart-traffic-light-03-firebase-adminsdk-mzf6v-45aa726e71.json"

    # Create and run traffic monitor
    monitor = TrafficMonitor(video_urls, model_path, firebase_credentials)
    monitor.run()

if __name__ == "__main__":
    main()