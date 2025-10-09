import json

def load_kbli_data(filepath="data/kbli_sample.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    data = load_kbli_data()
    print(f"Loaded {len(data)} KBLI entries")
    for d in data:
        print(f"{d['kbli']} - {d['judul']}")
