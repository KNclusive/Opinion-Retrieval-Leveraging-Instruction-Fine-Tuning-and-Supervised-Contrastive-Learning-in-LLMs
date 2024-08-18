import json
import re

with open(r'D:\MSAI\Thesis and Project\Perspectrum\Seperate_old\perspectrum_with_answers_v1.0.json', 'r') as f:
   all_data = json.load(f)

with open(r'D:\MSAI\Thesis and Project\Perspectrum\Seperate_old\perspective_pool_v1.0.json', 'r') as p:
   perspective_data = json.load(p)

with open(r'D:\MSAI\Thesis and Project\Perspectrum\Seperate_old\evidence_pool_v1.0.json', 'r') as p:
   evidence_data = json.load(p)

def clean_text(text):
   # Remove HTML tags
   text = re.sub(r'<[^>]+>', '', text)
   # Remove forward slashes
   text = re.sub(r'/', '', text)
   # Remove single quotes
   text = re.sub(r"'", '', text)
   # Remove double quotes
   text = re.sub(r'"', '', text)
   text = re.sub(r"’", "'", text)
   text = re.sub(r"‘", "'", text)
   text = re.sub(r"”", "'", text)
   text = re.sub(r"“", "'", text)
   if not text.endswith('.'):
      text += '.'
   # Remove extra whitespace
   text = ' '.join(text.split())
   return text

# map_polarity = {'UNDERMINE':0, 'SUPPORT':1}
perspective_data = {x["pId"]:clean_text(x["text"].strip()) for x in perspective_data}
evidence_data = {x["eId"]:clean_text(x["text"].strip()) for x in evidence_data}
def remove_elements(inp_dict):
   del inp_dict["cId"]
   del inp_dict["source"]
   del inp_dict["topics"]

   for temp in inp_dict["perspectives"]:
      if temp["stance_label_3"] == "not-a-perspective":
         print("Not-a-perspectivie", temp)
         del temp
         continue
      del temp["stance_label_5"]
      del temp["voter_counts"]
      temp["polarity"] = temp.pop("stance_label_3", "")
      temp["perspectives"] = list(map(lambda x: perspective_data[x], temp["pids"]))
      temp["context"] = list(map(lambda x: evidence_data[x], temp["evidence"]))
      del temp["pids"]
      del temp["evidence"]

   vac_dict = {}
   for temp in inp_dict["perspectives"]:
      pol = temp["polarity"]
      vac_dict.setdefault(pol, {})
      vac_dict[pol].setdefault('opinions', []).extend([x for x in temp['perspectives'] if x not in vac_dict[pol]['opinions']])
      vac_dict[pol].setdefault('context', []).extend([x for x in temp['context'] if x not in vac_dict[pol]['context']])
   inp_dict["perspectives"] = vac_dict

   return inp_dict

final_data = list(map(remove_elements, all_data))

with open("perspectrum.jsonl", 'w', encoding='utf-8') as d:
   for grp in final_data:
      d.write(json.dumps({'Claim':clean_text(grp["text"]),'Perspectives':grp["perspectives"]}, ensure_ascii=False) + '\n')