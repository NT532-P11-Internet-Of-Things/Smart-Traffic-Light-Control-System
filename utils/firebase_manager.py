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
                    'lanes': {
                        str(i): {
                            'is_green': i in [2, 4],
                            'remaining_time': 10,
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

    def update_lane_status(self, intersection_id, lane_id, status_data):
        """Update lane status in Firebase"""
        lane_ref = self.ref.child(f'intersections/{intersection_id}/lanes/{str(lane_id)}')
        lane_ref.update(status_data)