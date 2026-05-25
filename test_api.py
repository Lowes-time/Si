"""API 联调：记录 CRUD 与计算接口"""

import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8000"


def post_json(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(path):
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def delete(path):
    req = urllib.request.Request(BASE + path, method="DELETE")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_csv_sample(path):
    import csv
    wl, ref = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            wn = float(row[0])
            r = float(row[1])
            wl.append(10000.0 / wn)
            ref.append(r / 100.0 if r > 2 else r)
    return wl, ref


def test_health():
    data = get_json("/")
    assert data.get("status") == "running", data
    print("[OK] health check")


def test_materials():
    data = get_json("/api/materials")
    assert data["success"] and len(data["data"]) >= 2
    print("[OK] materials:", len(data["data"]))


def test_calculate(sample_path):
    wl, ref = load_csv_sample(sample_path)
    data = post_json("/api/calculate", {
        "wavelength": wl,
        "reflectance": ref,
        "material": "SIC",
        "theta_deg": 10.0,
    })
    assert data["success"], data.get("error")
    t = data["result"]["thickness_um"]
    print(f"[OK] calculate {sample_path}: thickness={t} um, R2={data['result']['r_squared']}")
    return data["result"]


def test_records(calc_result):
    payload = {
        "film_code": "TEST-AUTO-001",
        "material_type": "SIC",
        "thickness_um": calc_result["thickness_um"],
        "r_squared": calc_result["r_squared"],
        "multi_beam_level": calc_result["multi_beam_level"],
        "theta_deg": 10.0,
        "notes": "auto test",
        "optical_data": [
            {
                "wavelength": calc_result["wavelength"][i],
                "reflectance": calc_result["reflectance"][i],
                "fitted_reflectance": calc_result["ref_fit"][i],
                "seq_order": i,
            }
            for i in range(min(50, len(calc_result["wavelength"])))
        ],
    }
    created = post_json("/api/records/", payload)
    rid = created["id"]
    print("[OK] create record id=", rid)

    listing = get_json("/api/records/?search=TEST-AUTO")
    assert listing["total"] >= 1
    print("[OK] list records total=", listing["total"])

    detail = get_json(f"/api/records/{rid}")
    assert detail["film_code"] == "TEST-AUTO-001"
    print("[OK] record detail")

    req = urllib.request.Request(BASE + f"/api/records/{rid}/report")
    with urllib.request.urlopen(req, timeout=30) as resp:
        pdf = resp.read()
    assert pdf[:4] == b"%PDF"
    print("[OK] pdf report bytes=", len(pdf))

    delete(f"/api/records/{rid}")
    print("[OK] delete record")


def main():
    time.sleep(1)
    try:
        test_health()
        test_materials()
        calc = test_calculate("test_sic_15um.csv")
        test_records(calc)
        print("\nALL TESTS PASSED")
    except Exception as e:
        print("\nFAILED:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
