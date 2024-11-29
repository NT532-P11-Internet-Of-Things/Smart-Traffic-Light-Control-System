import time

class TrafficScheduler:
    def __init__(self, num_lanes=4):
        self.lanes = [
            {'id': 1, 'vehicles': 0, 'is_green': False, 'count': 0},
            {'id': 2, 'vehicles': 0, 'is_green': True, 'count': 0},
            {'id': 3, 'vehicles': 0, 'is_green': False, 'count': 0},
            {'id': 4, 'vehicles': 0, 'is_green': True, 'count': 0}
        ]
        self.standard_duration = 10  # Standard green light duration
        self.base_green_time = 10
        self.max_green_time = 30
        self.min_green_time = 5

    def getLanes(self):
        """Return the list of lanes"""
        return self.lanes

    def lanesTurn(self):
        """Determine the current lane that should get a turn"""
        # Find the first lane that is not green
        for lane in self.lanes:
            if not lane['is_green']:
                return lane
        # If all lanes are red, return the first lane
        return self.lanes[0]

    def enque(self, lane):
        """Move the given lane to the end of the queue"""
        # Rotate the lanes to put the current lane at the end
        lane_index = next((i for i, l in enumerate(self.lanes) if l == lane), -1)
        if lane_index != -1:
            self.lanes = self.lanes[lane_index + 1:] + self.lanes[:lane_index + 1]

    def update_lane_vehicles(self, lane_id, vehicle_count):
        """Update vehicle count for a specific lane"""
        for lane in self.lanes:
            if lane['id'] == lane_id:
                lane['vehicles'] = vehicle_count
                lane['count'] += 1  # Increment count to track lane usage
                break

    def switch_traffic_lights(self, lane_timers):
        """Switch traffic lights for opposite lane pairs and set green/red durations"""
        opposite_pairs = [(1, 3), (2, 4)]

        for pair in opposite_pairs:
            lane1, lane2 = pair
            lane1_obj = next((lane for lane in self.lanes if lane['id'] == lane1), None)
            lane2_obj = next((lane for lane in self.lanes if lane['id'] == lane2), None)

            timer1 = lane_timers[lane1 - 1]
            timer2 = lane_timers[lane2 - 1]

            if timer1.ready_to_switch and timer2.ready_to_switch:
                timer1.ready_to_switch = False
                timer2.ready_to_switch = False

                # Đảm bảo cả hai làn đều chuyển trạng thái
                lane1_obj['is_green'] = not lane1_obj['is_green']
                lane2_obj['is_green'] = not lane2_obj['is_green']

                green_time, red_time = self.schedule()

                # Cập nhật thời gian cho cả hai làn với thời gian giống nhau
                lane_timers[lane1 - 1].green_time = green_time
                lane_timers[lane1 - 1].remaining_time = green_time
                lane_timers[lane2 - 1].green_time = green_time
                lane_timers[lane2 - 1].remaining_time = green_time

                # Đặt lại thời gian bắt đầu
                lane_timers[lane1 - 1].start_time = time.time()
                lane_timers[lane2 - 1].start_time = time.time()

        return self.lanes

    def schedule(self):
        """Synchronize green times for opposite lane pairs"""
        max_green_time = 0
        pairs = [(self.lanes[0], self.lanes[2]), (self.lanes[1], self.lanes[3])]

        for pair in pairs:
            # Tính thời gian đèn xanh dựa trên làn có nhiều xe nhất trong cặp
            vehicles = max(pair[0]['vehicles'], pair[1]['vehicles'])
            print("số lượng xe đc tính:", vehicles)
            green_time = round(self.standard_duration + vehicles * 0.5, 0)
            green_time = max(self.min_green_time, min(green_time, self.max_green_time))
            print("thời gian greentime:", green_time)

            # Luôn lấy thời gian đèn xanh lớn nhất cho cả hai cặp làn
            max_green_time = max(max_green_time, green_time)

        # Cả hai cặp làn sẽ có thời gian đèn xanh giống nhau
        red_time = max_green_time + 3

        return max_green_time, red_time