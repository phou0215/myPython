from datetime import datetime
from datetime import timedelta

date1 = datetime.strptime('20210410', "%Y%m%d").date()
date2 = datetime.strptime('20210407', "%Y%m%d").date()
days = date1 - date2
print(days.days)
