import requests

BASE = "http://127.0.0.1:5000/"

data = [
    {"title": "Sandwich", "section": ["Lunch"], "modifiers": ["no pickles", "no mayo"]},
    {"title": "Pizza", "section": ["Dinner"], "modifiers": ["extra cheese", "gluten free"]},
    {"title": "Soup", "section": ["Lunch", "Dinner"], "modifiers": ["saltines", "no spoon"]},
]

for i in range(len(data)):
    response = requests.put(BASE + f"item/{i+1}", {"title": data[i]["title"], "section": data[i]["section"], "modifiers": data[i]["modifiers"]})
    # print(response.json())
    
input()
response = requests.patch(BASE + "item/1", {"title": "patched_name", "section": ["Dinner"], "modifiers": ["none"]})
print(response.json())
input()
response = requests.delete(BASE + "item/1")
print(response.json())
input()
response = requests.get(BASE + "item")
print(response.json())