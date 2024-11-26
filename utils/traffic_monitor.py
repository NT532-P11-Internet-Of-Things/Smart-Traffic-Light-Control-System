import cv2
import numpy as np
import time
from yolov8 import YOLOv8
from cap_from_youtube import cap_from_youtube


class TrafficScheduler:
    def __init__(self, num_lanes=4):
        self.lanes = [
            {'id': 1, 'vehicles': 0, 'is_green': False, 'time_ready': False},
            {'id': 2, 'vehicles': 0, 'is_green': True, 'time_ready': False},
            {'id': 3, 'vehicles': 0, 'is_green': False, 'time_ready': False},
            {'id': 4, 'vehicles': 0, 'is_green': True, 'time_ready': False}
        ]
        self.base_green_time = 10  # Base green light duration
        self.max_green_time = 30  # Maximum green light duration
        self.min_green_time = 5  # Minimum green light duration

    def update_lane_vehicles(self, lane_id, vehicle_count):
        """Update vehicle count for a specific lane"""
        for lane in self.lanes:
            if lane['id'] == lane_id:
                lane['vehicles'] = vehicle_count
                break

    def get_scheduling_time(self, lane_id):
        """Calculate green light time based on vehicle count"""
        # Find the lane
        current_lane = next((lane for lane in self.lanes if lane['id'] == lane_id), None)
        if not current_lane:
            return self.base_green_time

        # Calculate dynamic green time
        vehicle_factor = current_lane['vehicles']
        dynamic_time = min(
            max(
                self.base_green_time + (vehicle_factor * 0.5),
                self.min_green_time
            ),
            self.max_green_time
        )

        return round(dynamic_time)

    def switch_traffic_lights(self, lane_timers):
        """Switch traffic lights for opposite lane pairs"""
        # Opposite lane pairs: 1-3 and 2-4
        opposite_pairs = [(1, 3), (2, 4)]

        for pair in opposite_pairs:
            lane1, lane2 = pair

            # Find the lanes in the lanes list
            lane1_obj = next((lane for lane in self.lanes if lane['id'] == lane1), None)
            lane2_obj = next((lane for lane in self.lanes if lane['id'] == lane2), None)

            # Check the timers of a pair of opposite lanes
            timer1 = lane_timers[lane1 -1]
            timer2 = lane_timers[lane2 -1]

            # Switch their green status
            if timer1.ready_to_switch and timer2.ready_to_switch:
                timer1.ready_to_switch = False
                timer2.ready_to_switch = False

                lane1_obj['is_green'] = not lane1_obj['is_green']
                lane2_obj['is_green'] = not lane2_obj['is_green']

                # Tính toán thời gian mới dựa trên số lượng xe
                lane1_green_time = self.get_scheduling_time(lane1)
                lane2_green_time = self.get_scheduling_time(lane2)

                lane_timers[lane1 - 1].green_time = lane1_green_time
                lane_timers[lane2 - 1].green_time = lane2_green_time

                # Reset timer
                lane_timers[lane1 - 1].remaining_time = lane1_green_time
                lane_timers[lane2 - 1].remaining_time = lane2_green_time
                lane_timers[lane1 - 1].start_time = time.time()
                lane_timers[lane2 - 1].start_time = time.time()

        return self.lanes


class LaneTimer:
    def __init__(self, green_time=10):
        self.green_time = green_time
        self.remaining_time = green_time
        self.start_time = time.time()
        self.is_green = True
        self.ready_to_switch = False

    def update(self):
        """Update timer and check if ready to switch"""
        elapsed_time = time.time() - self.start_time
        self.remaining_time = max(0, self.green_time - elapsed_time)

        if self.remaining_time <= 0:
            self.ready_to_switch = True
            return True
        return False


class TrafficMonitor:
    def __init__(self, video_urls, model_path):
        self.video_urls = video_urls
        self.vehicle_classes = {
            2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
        }
        self.vehicle_counts_at_change = [0] * len(video_urls)

        # Setup YOLO model
        self.yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)

        # Setup video captures
        self.caps = self.setup_video_captures()

        # Determine uniform frame size
        self.frame_width, self.frame_height = self.get_uniform_frame_size()

        # Initialize traffic scheduler
        self.traffic_scheduler = TrafficScheduler()

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

            # Update traffic scheduler
            self.traffic_scheduler.update_lane_vehicles(i + 1, vehicle_count)

            # Check if lane timer needs update
            if lane_timer.update():
                # Lưu lại số xe tại thời điểm chuyển đèn
                self.vehicle_counts_at_change[i] = vehicle_count

                # Switch traffic lights for opposite lanes
                updated_lanes = self.traffic_scheduler.switch_traffic_lights(self.lane_timers)

                # Update lane timers based on vehicle count
                for j, lane in enumerate(updated_lanes):
                    new_green_time = self.traffic_scheduler.get_scheduling_time(lane['id'])
                    self.lane_timers[j].green_time = new_green_time
                    self.lane_timers[j].remaining_time = new_green_time

            # Get current lane state from scheduler
            lane_state = next((lane for lane in self.traffic_scheduler.lanes if lane['id'] == i + 1), None)
            is_green = lane_state['is_green'] if lane_state else False

            # Draw detections
            detection_frame = self.yolov8_detector.draw_detections(frame)

            # Add lane number and vehicle count
            cv2.putText(detection_frame, f"Lane {i + 1}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(detection_frame, f"Vehicles: {vehicle_count}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(detection_frame, f"Vehicles at Light Change: {self.vehicle_counts_at_change[i]}", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

            # Display remaining time for each lane
            time_text = f"Time: {max(0, int(lane_timer.remaining_time))}s"
            color = (0, 255, 0) if is_green else (0, 0, 255)
            status = "Green" if is_green else "Red"
            cv2.putText(detection_frame, f"{status} Light: {time_text}", (10, 110),
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