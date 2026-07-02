import sys
sys.path.insert(0, r'd:\0_trea_projects_by_bela\price_dashboard\01_Build')
from data_loader import get_data_for_frontend

try:
    data = get_data_for_frontend()
    print(f"Data loaded: {len(data['price_data'])} records")
    print(f"Materials: {len(data['materials'])}")
    print(f"Date range: {data['date_range']}")
except Exception as e:
    print(f"Error: {e}")
