class Lanes:
    def __init__(self):
        self.lanes = []

    def add_lane(self, lane):
        self.lanes.append(lane)

    def getLanes(self):
        return self.lanes

    def lanesTurn(self):
        # Return the lane with the most vehicles (first in the list if tie)
        return max(self.lanes, key=lambda lane: lane.count)

    def enque(self, lane):
        # Move the current turn lane to the end
        self.lanes.remove(lane)
        self.lanes.append(lane)


class Lane:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.vehicle_types = {}


def schedule(lanes):
    """
    Calculate traffic light scheduling based on vehicle count

    Args:
    lanes (Lanes): Object containing lane information

    Returns:
    float: Scheduled green light time
    """
    standard = 10  # standard duration
    reward = 0  # reward to be added or subtracted on the standard duration
    turn = lanes.lanesTurn()

    for i, lane in enumerate(lanes.getLanes()):
        if i == (len(lanes.getLanes()) - 1):
            reward = reward + (turn.count - lane.count) * 0.2
        else:
            reward = reward + (turn.count - lane.count) * 0.5

    scheduled_time = round((standard + reward), 0)
    lanes.enque(turn)
    return scheduled_time