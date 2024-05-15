import datetime
import json
from service.rubbish_tracker_service import RubbishTrackerService


service = RubbishTrackerService()

report = service.getReport("66323827836e1e85e22c679a")

rightnowUTC = rightnowUTC = service.getRightnowUTC()

with open('rubbish_tracker_get_report_out_' + str(rightnowUTC) + '.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=4)