import csv, requests, os
RASA_URL = os.getenv("RASA_URL", "http://localhost:5005/model/parse")

def load_eval(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def main():
    rows = load_eval("eval/eval_set.csv")
    correct = 0
    total = len(rows)
    for r in rows:
        text = r["text"]
        resp = requests.post(RASA_URL, json={"text": text}).json()
        intent = resp["intent"]["name"]
        print(text, "->", intent)
        if intent == r["intent"]:
            correct += 1
    print(f"Accuracy: {correct}/{total} = {correct/total*100:.2f}%")

if __name__ == "__main__":
    main()
