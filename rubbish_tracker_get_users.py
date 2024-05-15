import datetime
import json
from service.rubbish_tracker_service import RubbishTrackerService


service = RubbishTrackerService()

users = service.getUsers()

rightnowUTC = rightnowUTC = service.getRightnowUTC()

with open('rubbish_tracker_get_users_out_' + str(rightnowUTC) + '.json', 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=4)