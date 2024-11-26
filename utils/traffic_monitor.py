import cv2
import numpy as np
import time
from yolov8 import YOLOv8
from cap_from_youtube import cap_from_youtube


class LaneTimer:
    def __init__(self, green_time=10):
        self.green_time = green_time
        self.remaining_time = green_time
        self.start_time = time.time()
        self.is_green = True

    def update(self):
        """Update timer and return whether to switch lights"""
        elapsed_time = time.time() - self.start_time
        self.remaining_time = self.green_time - elapsed_time

        if self.remaining_time <= 0:
            self.is_green = not self.is_green
            self.start_time = time.time()
            self.remaining_time = self.green_time
            return True
        return False


class TrafficMonitor:
    def __init__(self, video_urls, model_path):
        self.video_urls = video_urls
        self.vehicle_classes = {
            2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
        }

        # Setup YOLO model
        self.yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)

        # Setup video captures
        self.caps = self.setup_video_captures()

        # Determine uniform frame size
        self.frame_width, self.frame_height = self.get_uniform_frame_size()

        # Initialize lane timers
        self.lane_timers = [LaneTimer() for _ in range(len(video_urls))]

    def setup_video_captures(self):
        """Set up video captures with error handling"""
        caps = []
        for url in self.video_urls:
            try:
                cap = cap_from_youtube(url, resolution='720p')
                caps.append(cap)
            except Exception as e:
                print(f"Error capturing video {url}: {e}")
        return caps

    def get_uniform_frame_size(self):
        """Determine a uniform frame size for all videos"""
        if self.caps:
            first_cap = self.caps[0]
            width = int(first_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(first_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Ensure divisible by 2 for easier splitting
            width = width if width % 2 == 0 else width - 1
            height = height if height % 2 == 0 else height - 1

            return width, height

        # Fallback size
        return 1280, 720

    def create_grid_frame(self, frames):
        """Create a grid frame from input frames"""
        # Resize all frames to uniform size
        resized_frames = [cv2.resize(frame, (self.frame_width, self.frame_height))
                          for frame in frames]

        # Create a 2x2 grid
        top_row = np.hstack((resized_frames[0], resized_frames[1]))
        bottom_row = np.hstack((resized_frames[2], resized_frames[3]))

        combined_frame = np.vstack((top_row, bottom_row))

        return combined_frame

    def process_lanes(self, frames):
        """Process lanes and return detection frames with lane info"""
        detection_frames = []
        lane_counts = []

        for i, (frame, lane_timer) in enumerate(zip(frames, self.lane_timers)):
            # Detect objects
            boxes, scores, class_ids = self.yolov8_detector(frame)

            # Count vehicles
            vehicle_count = sum(1 for class_id in class_ids if class_id in self.vehicle_classes)
            lane_counts.append(vehicle_count)

            # Draw detections
            detection_frame = self.yolov8_detector.draw_detections(frame)

            # Add lane number and vehicle count
            cv2.putText(detection_frame, f"Lane {i + 1}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(detection_frame, f"Vehicles: {vehicle_count}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Display remaining time for each lane
            time_text = f"Time: {max(0, int(lane_timer.remaining_time))}s"
            color = (0, 255, 0) if lane_timer.is_green else (0, 0, 255)
            cv2.putText(detection_frame, time_text, (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            detection_frames.append(detection_frame)

        return detection_frames, lane_counts

    def run(self):
        """Main monitoring loop"""
        cv2.namedWindow("Traffic Monitoring", cv2.WINDOW_NORMAL)

        while all(cap.isOpened() for cap in self.caps):
            # Check for quit
            if cv2.waitKey(1) == ord('q'):
                break

            # Read frames
            frames = []
            for cap in self.caps:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)

            if len(frames) < 4:
                break

            # Update lane timers
            for lane_timer in self.lane_timers:
                lane_timer.update()

            # Process lanes
            detection_frames, lane_counts = self.process_lanes(frames)

            # Create grid frame
            combined_frame = self.create_grid_frame(detection_frames)

            # Show frame
            cv2.imshow("Traffic Monitoring", combined_frame)

        # Cleanup
        for cap in self.caps:
            cap.release()
        cv2.destroyAllWindows()