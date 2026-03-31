
import json
import re

def extract_json(raw_response):
    raw_response = raw_response.strip()
    # Robust JSON extraction logic from ai_service.py
    json_match = re.search(r'(\{.*\}|\[.*\])', raw_response, re.DOTALL)
    if json_match:
        response_text = json_match.group(1)
    else:
        response_text = raw_response

    if response_text.startswith("```"):
        lines = response_text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        response_text = "\n".join(lines).strip()
    
    return json.loads(response_text)

def test_parsing():
    test_cases = [
        {
            "name": "Standard Markdown",
            "input": "Here is the JSON:\n```json\n{\"plan\": []}\n```\nHope this helps!",
            "expected": {"plan": []}
        },
        {
            "name": "Preamble and post-text",
            "input": "Sure! Here is your plan: {\"day\": 1} Enjoy!",
            "expected": {"day": 1}
        },
        {
            "name": "Nested JSON with text",
            "input": "Random text {\"outer\": {\"inner\": [1, 2, 3]}} more text",
            "expected": {"outer": {"inner": [1, 2, 3]}}
        },
        {
            "name": "Array JSON",
            "input": "Plan list: [{\"id\": 1}, {\"id\": 2}] end.",
            "expected": [{"id": 1}, {"id": 2}]
        }
    ]

    for case in test_cases:
        try:
            result = extract_json(case["input"])
            assert result == case["expected"]
            print(f"PASS: {case['name']}")
        except Exception as e:
            print(f"FAIL: {case['name']} - Error: {e}")
            print(f"  Input: {case['input']}")
            print(f"  Result: {result if 'result' in locals() else 'N/A'}")

if __name__ == "__main__":
    test_parsing()
