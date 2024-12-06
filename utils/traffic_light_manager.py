import time
from .firebase_manager import FirebaseManager

MIN_GREEN_TIME = 5
MAX_GREEN_TIME = 30
BASE_GREEN_TIME = 10
REWARD_MULTIPLIER = 0.5

class TrafficLightManager:
    def __init__(self, num_lanes=4, firebase_manager=None):
        self.firebase = firebase_manager
        self.intersection_id = 'main_intersection'
        self.lanes = [
            {
                'id': lane_id,
                'is_green': lane_id in [2, 4],  # True/False: Mặc định làn 2 và 4 có đèn xanh
                'green_time': BASE_GREEN_TIME,  # Thời gian đèn xanh mặc định
                'red_time': BASE_GREEN_TIME + 3,  # Thời gian đèn đỏ mặc định
                'remaining_time': BASE_GREEN_TIME,  # Thời gian còn lại của đèn
                'start_time': time.time(),  # Thời điểm bắt đầu lượt
                'vehicles_at_change': 0,  # Số xe tại thời điểm chuyển đèn
                'total_vehicles': 0,  # Tổng số xe trong làn
                'cycle_count': 0,  # Số lần chu kỳ đèn giao thông
                'ready_to_switch': False,
            } for lane_id in range(1, num_lanes + 1)
        ]
        self.opposite_pairs = [(1, 3), (2, 4)]

    def update_timers(self):
        """Update all lane timers and check if ready to switch"""
        current_time = time.time()
        all_ready = True

        for lane in self.lanes:
            elapsed_time = current_time - lane['start_time']
            target_time = lane['green_time'] if lane['is_green'] else lane['red_time']
            lane['remaining_time'] = round(max(0, target_time - elapsed_time))

            if lane['remaining_time'] <= 0:
                lane['ready_to_switch'] = True
            else:
                all_ready = False

            # Update Firebase with new remaining time
            if self.firebase:
                status_data = {
                    'remaining_time': lane['remaining_time'],
                    'green_time': lane['green_time'],
                    'last_update': int(current_time)
                }
                self.firebase.update_lane_status(
                    self.intersection_id,
                    lane['id'],
                    status_data
                )

        return all_ready

    def update_lane(self, lane_id, vehicles_count):
        """Cập nhật thông tin xe và trạng thái cho một làn"""
        for lane in self.lanes:
            if lane['id'] == lane_id:
                lane['total_vehicles'] = vehicles_count

                # Update Firebase if available
                if self.firebase:
                    status_data = {
                        'vehicle_count': vehicles_count,
                        'is_green': lane['is_green'],
                        'remaining_time': lane['remaining_time'],
                        'green_time': lane['green_time'],
                        'last_update': int(time.time())
                    }
                    self.firebase.update_lane_status(
                        self.intersection_id,
                        lane_id,
                        status_data
                    )
                break

    def update_vehicle_at_change(self, lane_id, vehicles_at_change):
        """Cập nhật thông tin xe và trạng thái cho một làn"""
        for lane in self.lanes:
            if lane['id'] == lane_id:
                lane['vehicles_at_change'] = vehicles_at_change
                lane['cycle_count'] += 1
                break
    def switch_traffic_lights(self):
        """Chuyển trạng thái đèn giao thông cho các làn đối diện"""
        green_time = self.schedule()

        for pair in self.opposite_pairs:
            lane1, lane2 = pair
            lane1_obj = next(lane for lane in self.lanes if lane['id'] == lane1)
            lane2_obj = next(lane for lane in self.lanes if lane['id'] == lane2)

            # Cập nhật thời gian và số xe tại thời điểm chuyển
            for lane in [lane1_obj, lane2_obj]:
                lane['is_green'] = not lane['is_green']
                lane['green_time'] = green_time
                lane['red_time'] = green_time + 3
                lane['remaining_time'] = lane['green_time'] if lane['is_green'] else lane['red_time']
                lane['start_time'] = time.time()
                lane['vehicles_at_change'] = lane['total_vehicles']
                lane['cycle_count'] += 1
                lane['ready_to_switch'] = False

                # Update Firebase if available
                if self.firebase:
                    status_data = {
                        'is_green': lane['is_green'],
                        'remaining_time': lane['remaining_time'],
                        'green_time': lane['green_time'],
                        'vehicle_count': lane['total_vehicles'],
                        'last_update': int(time.time())
                    }
                    self.firebase.update_lane_status(
                        self.intersection_id,
                        lane['id'],
                        status_data
                    )

        return self.lanes

    def schedule(self):
        """Synchronize green times for opposite lane pairs"""
        # Duyệt qua từng cặp làn đối diện
        current_red_pair = None
        for pair in self.opposite_pairs:
            # Lấy đối tượng làn dựa trên ID
            lane1_obj = next(lane for lane in self.lanes if lane['id'] == pair[0])
            lane2_obj = next(lane for lane in self.lanes if lane['id'] == pair[1])

            # Kiểm tra xem trạng thái đèn xanh của cả hai làn
            if not lane1_obj['is_green'] and not lane2_obj['is_green']:
                current_red_pair = (lane1_obj, lane2_obj)
                break
        if not current_red_pair:
            return BASE_GREEN_TIME

        # Get all vehicle counts for comparison
        all_vehicle_counts = [lane['total_vehicles'] for lane in self.lanes]
        avg_other_lanes = sum(all_vehicle_counts) / len(all_vehicle_counts)

        # Calculate rewards for both lanes in the current red pair
        lane1, lane2 = current_red_pair
        lane1_vehicles = lane1['total_vehicles']
        lane2_vehicles = lane2['total_vehicles']

        # Calculate reward based on difference from average
        lane1_reward = (lane1_vehicles - avg_other_lanes) * REWARD_MULTIPLIER
        lane2_reward = (lane2_vehicles - avg_other_lanes) * REWARD_MULTIPLIER

        # Use the maximum reward from the pair
        max_reward = max(lane1_reward, lane2_reward)

        # Calculate final green time
        green_time = BASE_GREEN_TIME + max_reward
        # Ensure green time stays within bounds
        green_time = round(min(max(green_time, MIN_GREEN_TIME), MAX_GREEN_TIME))

        print(f"Vehicle counts - Lane {lane1['id']}: {lane1_vehicles}, Lane {lane2['id']}: {lane2_vehicles}")
        print(f"Average vehicles in other lanes: {avg_other_lanes:.2f}")
        print(f"Reward: {max_reward:.2f}")
        print(f"Final green time: {green_time}")

        return green_time

    def update_remaining_time(self):
        """Cập nhật thời gian còn lại cho mỗi làn"""
        current_time = time.time()
        for lane in self.lanes:
            elapsed_time = current_time - lane['start_time']

            if lane['is_green']:
                lane['remaining_time'] = max(0, lane['green_time'] - elapsed_time)
                if lane['remaining_time'] <= 0:
                    lane['start_time'] = current_time
                    lane['remaining_time'] = lane['red_time']
            else:
                lane['remaining_time'] = max(0, lane['red_time'] - elapsed_time)
                if lane['remaining_time'] <= 0:
                    lane['start_time'] = current_time
                    lane['remaining_time'] = lane['green_time']

    def get_lane_status(self, lane_id):
        """Lấy trạng thái chi tiết của một làn"""
        for lane in self.lanes:
            if lane['id'] == lane_id:
                return lane
        return None

    def get_all_lanes_status(self):
        """Lấy trạng thái của tất cả các làn"""
        return self.lanes

    def switch_traffic_lights_immediately(self):
        """Chuyển trạng thái đèn giao thông về đèn vàng để chuẩn bị chuyển đèn"""
        for pair in self.opposite_pairs:
            lane1, lane2 = pair
            lane1_obj = next(lane for lane in self.lanes if lane['id'] == lane1)
            lane2_obj = next(lane for lane in self.lanes if lane['id'] == lane2)

            # Cập nhật thời gian và số xe tại thời điểm chuyển
            for lane in [lane1_obj, lane2_obj]:
                lane['remaining_time'] = 0 if lane['is_green'] else 3

                # Update Firebase if available
                if self.firebase:
                    status_data = {
                        'remaining_time': lane['remaining_time'],
                        'vehicle_count': lane['total_vehicles'],
                        'last_update': int(time.time())
                    }
                    self.firebase.update_lane_status(
                        self.intersection_id,
                        lane['id'],
                        status_data
                    )

        return self.lanes
