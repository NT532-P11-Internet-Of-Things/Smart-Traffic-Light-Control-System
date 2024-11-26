from utils import TrafficMonitor

def main():
    # Video URLs for 4 lanes
    video_urls = [
        'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
        'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
        'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_',
        'https://youtu.be/MNn9qKG2UFI?si=tYXsHABuQHSVUAv_'
    ]

    # Path to YOLO model
    model_path = "models/yolov8m.onnx"

    # Create and run traffic monitor
    monitor = TrafficMonitor(video_urls, model_path)
    monitor.run()

if __name__ == "__main__":
    main()