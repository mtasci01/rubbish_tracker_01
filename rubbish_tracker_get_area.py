import json
from service.rubbish_tracker_service import RubbishTrackerService


service = RubbishTrackerService()

area = service.getArea("6636a276067a84bae086dd20")

rightnowUTC = rightnowUTC = service.getRightnowUTC()

with open('rubbish_tracker_get_area_out_' + str(rightnowUTC) + '.json', 'w', encoding='utf-8') as f:
    json.dump(area, f, ensure_ascii=False, indent=4)