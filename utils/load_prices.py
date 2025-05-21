import sys
from pathlib import Path
from datetime import datetime

# Get the parent folder (one level up)
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from pricing import refresh_prices

history = 3

print(f"--------------------------------------------------------------------------")
time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"Loading of prices started at {time_now} \n")

#refresh_prices(history,symbol='CSPX.L')
refresh_prices(history)

time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"\nFinished at {time_now}")