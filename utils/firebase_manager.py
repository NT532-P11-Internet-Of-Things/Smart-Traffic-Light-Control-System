# firebase_manager.py
from firebase_admin import credentials, initialize_app, db
import time


class FirebaseManager:
    def __init__(self, credential_path):
        # Initialize Firebase
        cred = credentials.Certificate(credential_path)
        initialize_app(cred, {
            'databaseURL': 'https://smart-traffic-light-03-default-rtdb.asia-southeast1.firebasedatabase.app'
        })
        self.ref = db.reference('traffic_system')
        self._setup_initial_data()

    def _setup_initial_data(self):
        """Initialize default data structure in Firebase"""
        default_data = {
            'intersections': {
                'main_intersection': {
                    'isAuto': True,
                    'lanes': {
                        str(i): {
                            'is_green': i in [2, 4],
                            'remaining_time': 10,
                            'green_time': 10,
                            'vehicle_count': 0,
                            'last_update': time.time()
                        } for i in range(1, 5)
                    }
                }
            }
        }
        # Update if not exists
        if not self.ref.get():
            self.ref.set(default_data)

    def is_auto_mode(self, intersection_id):
        """Check if intersection is in auto mode"""
        return self.ref.child(f'intersections/{intersection_id}/isAuto').get()

    def is_need_sync(self, intersection_id):
        return self.ref.child(f'intersections/{intersection_id}/needSync').get()

    def update_lane_status(self, intersection_id, lane_id, status_data):
        """Update lane status in Firebase based on auto mode"""
        lane_ref = self.ref.child(f'intersections/{intersection_id}/lanes/{str(lane_id)}')

        # Always update vehicle count regardless of auto mode
        if 'vehicle_count' in status_data:
            lane_ref.update({
                'vehicle_count': status_data['vehicle_count'],
                'last_update': status_data['last_update']
            })

        # Update other status data only if in auto mode
        if self.is_auto_mode(intersection_id):
            # Create a new dict excluding vehicle_count and last_update
            auto_status = {k: v for k, v in status_data.items()
                           if k not in ['vehicle_count', 'last_update']}
            if auto_status:  # Only update if there are other fields to update
                lane_ref.update(auto_status)