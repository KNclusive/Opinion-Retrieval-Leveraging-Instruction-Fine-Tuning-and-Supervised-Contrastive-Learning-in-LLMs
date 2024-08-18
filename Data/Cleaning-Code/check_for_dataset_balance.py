import json
with open('perspectrum_balanced_super_final.jsonl','r', encoding='utf-8') as p:
   data = p.readlines()

data = list(map(lambda x: json.loads(x), data))

def Check_balance(data):
   cnt = 0
   for dat in data:
      if "SUPPORT" not in dat["Perspectives"] or "UNDERMINE" not in dat["Perspectives"]:
         cnt+=1
         print(dat["Claim"])
   print(cnt)

Check_balance(data)