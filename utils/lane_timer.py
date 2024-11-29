import time

class LaneTimer:
    def __init__(self, green_time=10, red_time=13):
        self.green_time = green_time
        self.red_time = red_time
        self.remaining_time = green_time
        self.start_time = time.time()
        self.is_green = True
        self.ready_to_switch = False
        self.vehicle_count = 0

    def update(self):
        """Update timer and check if ready to switch"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.is_green:
            self.remaining_time = max(0, self.green_time - elapsed_time)
        else:
            self.remaining_time = max(0, self.red_time - elapsed_time)

        if self.remaining_time <= 0:
            self.ready_to_switch = True
            return True
        return False

    @staticmethod
    def update_all(lane_timers):
        """Update all LaneTimers and return True if all are ready to switch"""
        all_ready = True
        for timer in lane_timers:
            if not timer.update():
                all_ready = False
        return all_ready