import urllib.request
import json
import time

def test_api():
    base_url = "http://127.0.0.1:8000/api/records/"
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # 1. Test creating a record
    data = {
        "filename": "test_data.csv",
        "material": "Si",
        "thickness_um": 2.5,
        "r_squared": 0.99,
        "multi_beam_level": "None",
        "data_json": {
            "wavelength": [400.0, 450.0, 500.0],
            "reflectance": [0.1, 0.2, 0.3],
            "ref_fit": [0.11, 0.21, 0.31]
        }
    }
    
    req = urllib.request.Request(base_url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("Create Record Response:", res_data)
            record_id = res_data["id"]
    except Exception as e:
        print(f"Failed to create record: {e}")
        return
        
    # 2. Test reading records list
    req = urllib.request.Request(base_url)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("Read Records Response:", res_data)
    except Exception as e:
        print(f"Failed to read records: {e}")
        return

    # 3. Test reading specific record
    req = urllib.request.Request(f"{base_url}{record_id}")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("Read Single Record Response:", res_data)
            
            # Verify data
            if res_data["data"]["wavelength"] == [400.0, 450.0, 500.0]:
                print("SUCCESS: Data read correctly!")
            else:
                print("ERROR: Data mismatch!")
    except Exception as e:
        print(f"Failed to read single record: {e}")
        return

if __name__ == "__main__":
    test_api()
