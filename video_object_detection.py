# main.py
from utils import TrafficMonitor

def main():
    # Video URLs for 4 lanes
    video_urls = [
        'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
        'https://youtu.be/Kc-jyoCHZq8',
        'https://youtu.be/SqxQRLcUvf4',
        'https://youtu.be/xQlMXaL8yZs'
    ]

    # Path to YOLO model
    model_path = "models/yolov8m.onnx"
    firebase_credentials = "credential/smart-traffic-light-03-firebase-adminsdk-mzf6v-45aa726e71.json"

    # Create and run traffic monitor
    monitor = TrafficMonitor(video_urls, model_path, firebase_credentials)
    monitor.run()

if __name__ == "__main__":
    main()