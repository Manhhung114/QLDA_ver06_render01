from datetime import date
from cloud_db import calc_progress_status, calculate_delay_days

# Chưa hoàn thành, quá hạn 5 ngày
assert calc_progress_status('2026-08-01','2026-08-10',100,80,date(2026,8,15)) == 'Chậm tiến độ'
assert calculate_delay_days('2026-08-10',80,'',date(2026,8,15)) == 5

# Hoàn thành đúng/trước hạn
assert calc_progress_status('2026-08-01','2026-08-10',100,100,date(2026,8,10)) == 'Hoàn thành'
assert calculate_delay_days('2026-08-10',100,'2026-08-10',date(2026,8,20)) == 0

# Hoàn thành trễ 5 ngày: vẫn Hoàn thành, ngày trễ khóa ở 5
assert calc_progress_status('2026-08-01','2026-08-10',100,100,date(2026,8,15)) == 'Hoàn thành'
assert calculate_delay_days('2026-08-10',100,'2026-08-15',date(2026,8,30)) == 5

print('V3.6 delay logic: OK')
