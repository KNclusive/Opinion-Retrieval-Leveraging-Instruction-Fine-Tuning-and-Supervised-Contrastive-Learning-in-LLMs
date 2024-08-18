import json
import re
import os
import random
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading

rate_limit_lock = threading.Lock()
RATE_LIMIT_INTERVAL = 60  # 60 seconds interval
MAX_REQUESTS_PER_INTERVAL = 500  # Max 500 requests per minute
MAX_TOKENS_PER_INTERVAL = 30000  # Max 30,000 tokens per minute

request_count = 0
token_count = 0
daily_token_count = 0
start_time = time.time()
day_start_time = time.time()

def rate_limiter(token_usage):
   global request_count, token_count, daily_token_count, start_time, day_start_time
   with rate_limit_lock:
      current_time = time.time()
      elapsed_time = current_time - start_time
      day_elapsed_time = current_time - day_start_time

      # Reset interval counts if interval has passed
      if elapsed_time > RATE_LIMIT_INTERVAL:
         start_time = current_time
         request_count = 0
         token_count = 0

      # Reset daily count if a day has passed
      if day_elapsed_time > 86400:  # 86400 seconds in a day
         day_start_time = current_time
         daily_token_count = 0

      # Check if we need to wait due to request or token limits
      if request_count >= MAX_REQUESTS_PER_INTERVAL or token_count + token_usage > MAX_TOKENS_PER_INTERVAL: #or daily_token_count + token_usage > MAX_TOKENS_PER_DAY
         sleep_time = RATE_LIMIT_INTERVAL - elapsed_time
         print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
         time.sleep(max(sleep_time, 0))
         # Reset counts after sleep
         start_time = time.time()
         request_count = 0
         token_count = 0

      # Update counts
      request_count += 1
      token_count += token_usage
      daily_token_count += token_usage

os.environ['OpenAI_API'] = # Your OpenAI Access token here

# with open('perspectrum.jsonl','r', encoding='utf-8') as p:
#    data = p.readlines()

with open('perspectrum_balanced_NumMatch.jsonl','r', encoding='utf-8') as p:
   data = p.readlines()

data = list(map(lambda x: json.loads(x), data))
print("Data Loaded...\n")
client = OpenAI(api_key=os.environ.get('OpenAI_API'))
print("Client Created...\n")

example_claims_perspectives = [
   {
      'claim': "Vaccination must be made compulsory.",
      'perspectives': 
      {
         'SUPPORT': 
         {
            'opinions': ["It is the state's duty to protect its community.", "The state must keep its community safe.", "The safety of the community is the states priority.", "Compulsory vaccines are a financial relief on the health system.", "The impacts of unvaccinated populations stain the financial resources of the healthcare system.", "A fully vaccinated population lesses the financial stress of the health system.", "Duty to protect the child.", "Children must be protected.", "It is the duty of the state to protect children."]
         },
         'UNDERMINE': 
         {
            'opinions': ["Compulsory vaccination violates the individuals' right to bodily integrity.", "Individuals have the right to refuse vaccinations.", "Peoples bodies are there own, and they have the right to refuse to be vaccinated.", "It is a parental right to decide about vaccinations for a child.", "Parents have the right to make the decision about vaccinations for their children.", "By making vaccinations mandatory, it takes away the rights of the parent.", "Vaccines have severe side effects."]
         }
      }
   },
   {
      'claim': "All countries should have the right to pursue a nuclear defence.",
      'perspectives': 
      {
         'SUPPORT': 
         {
            'opinions': ["Small countries would be able to pursue their independence without having to rely on larger countries.", "Disarmament would actually cause increased insecurity among nations, it is near impossible to guarantee that a nation has disarmed.", "Small countries would no longer need the protection of larger ones, so could become more politically independent.", "Disarmament would actually cause increased insecurity among nations, you can never really know for sure whether they have disarmed.", "Disarmament would actually cause increased insecurity among nations, as there can never be any guarantee that a nation has disarmed.", "Thus the super power model will be broken and small countries will be finally given the chance to have political independence without the need of protection from a 'big brother'.", "All the people worldwide have the same rights and are equal to one another.", "The pursuit of nuclear defence (respectively the possession of nuclear weapons) by more countries is a guarantee for peace.", "Public acknowledgement of the right to nuclear deterrence will benefit the public regulation of nuclear weapons generally.", "Nuclear weapons give states valuable agenda-setting power on the international stage.", "Countries with nuclear weapons have the ability to set their own agenda.", "States with nuclear weapons are afforded more authority to set agendas at international levels.", "All countries have a right to defend themselves with nuclear weapons, even when they lack the capacity in conventional weapons.", "All states have a right to nuclear self-defense.", "To use nuclear weapons in defense of the nation is lawful for all countries.", "countries have to right to self defense with nuclear weapons, even when they lack capacity in conventional weapon.", "all countries are entitled to self defense with nuclear weapons, even when they do not have the capacity to carry conventional weapons.", "No country has an inherent right to invade or use aggression against another.", "Disarmament is impossible, rendering efforts to disarm pointless and simply wasteful.", "The abolition of nuclear weapons would actually incentivize the development and use of even more dangerous weapons, such as chemical and biological weapons."]
         },
         'UNDERMINE': 
         {
            'opinions': ["Humanitarian intervention becomes impossible in states that possess nuclear weapons.", "Humanitarian missions would not be possible in states that have nuclear weapons.", "It is very difficult to intercede in humanitarian crises in states wherein nuclear weapons are present.", "The threat of a state developing nuclear weapons could instigate pre-emptive strikes from its neighbours and rivals to prevent the acquisition of such weapons.", "Other countries could strike against those developing nuclear weapons to protect themselves.", "To keep other countries from obtaining a nuclear arsenal, other nations may pre-emptively strike.", "The intention of a state to develop nuclear weapons may incite military attacks by enemies and by other supporting countries.", "Possessing nuclear weapons will be counter to the peaceful interests of states.", "Nuclear weapons can fall into the wrong hands.", "Its conceivable that the wrong people will have the weapons.", "The nukes can end up being used against us.", "Terrorists will steal nuclear weapons from poorly guarded arsenals.", "[Iran specific] Iran has threatened to destroy Israel.", "Iran has Israel targeted.", "The United States has an obligation to protect international stability due to its unique military strength.", "The US must protect the international community.", "The US military is needed to ensure peace.", "[Iran specific] Others, particularly Israel, would act if the United States did not.", "If the US does not act on Iran, Israel will.", "Nuclear waste disposal is rarely safeefficient; it is too much to expect a sqeaky clean disposaldisarmament of nuclear weapons.", "Proliferation of nuclear weapons increases the chances of nuclear accidents.", "States will give terrorists nuclear weapons.", "Irrational leaders make the possession of nuclear weapons dangerous.", "It is immoral to use the threat of nuclear annihilation in order to achieve foreign policy aims."]
         }
      }
   },
   {
      'claim': "The right to anonymous posting on the internet should be protected by law.",
      'perspectives': 
      {
         'SUPPORT': 
         {
            'opinions': ["Internet anonymity allows people to speak the truth without fearing harm to their careers.", "Internet anonymity encourages honesty.", "Internet anonymity enables citizens to exercise their right to free speech.", "Anonymity online allows for free speech.", "Internet anonymity allows people to experiment and construct with new social identities.", "People are able to create new social identities when the internet is anonymous.", "The anonymity of the internet allows people to create new social identities for themselves."]
         },
         'UNDERMINE': 
         {
            'opinions': ["Internet anonymity leads to spam.", "Span proliferates with anonymity on the internet.", "Internet anonymity increases cyberbullying and trolling.", "Individuals are more likely to bully and troll when they are anonymous.", "Cyberbullying and trolling are more common when peoples internet activity is anonymous.", "Internet anonymity allows internet users to engage in illegal activities.", "When internet users are anonymous, they are more easily able to engage in illegal activities.", "There is less deterrance to illegal activities on the internet when people are able to remain anonymous."]
         }
      }
   }
]

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
   text = re.sub(r'\d+\.\s*', '', text)
   text = re.sub(r'\*\*.*?:\*\*|\*\*.*?\*\*: ?', '', text)
   text = text.strip()
   if not text.endswith('.'):
      text += '.'
   # Remove extra whitespace
   text = ' '.join(text.split())
   return text

def check_imbalance(data1):
   count = 0
   claims_to_ret = {}
   for dat in data:
      if "SUPPORT" not in dat["Perspectives"] or "UNDERMINE" not in dat["Perspectives"]:
         claims_to_ret[clean_text(dat['Claim'])] = {x: list(map(clean_text , dat["Perspectives"][x]['opinions'])) for x in list(dat['Perspectives'].keys())}
         count += 1
   return claims_to_ret

def get_avg_length(datas):
   count = 0
   claims_to_ret2 = {}
   for dat in datas:
      for subitm in dat['Perspectives']:
         calc_len = len(dat['Perspectives'][subitm]['opinions'])
         if calc_len <=5:
            text = clean_text(dat['Claim'])
            count+=1
            claims_to_ret2.setdefault(text, {})
            claims_to_ret2[text].setdefault(subitm, {})
            claims_to_ret2[text][subitm] = {'num': 7-calc_len, 'opinions': dat['Perspectives'][subitm]['opinions']}
   return claims_to_ret2

def generate_response(claim, typea, invtypea, perspectives):
   rate_limiter(500)
   sys_prompt = f"Given the Actual Claim: '{claim}' and {typea.lower()}ing perspectives: {"\n".join(perspectives)}, generate seven perspectives that are diverse and are {invtypea.lower()}ing the Actual Claim."
   # print(sys_prompt)

   # API call to generate responses
   response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
         {"role": "system", "content": 'You are a simple diverse perspective generator who fulfills the instruction following the example.'},
         {"role": "user", "content": sys_prompt}
         ],
      max_tokens=500,
   )
   return list(map(clean_text, [elem for elem in response.choices[0].message.content.split("\n") if elem.strip()]))

def generate_response_mod(claim, typea, num, perspectives):
   rate_limiter(500)
   print("Testing1", claim, typea)
   system_prompt = f"Given the Actual Claim: '{claim}' and Actual perspectives: {"\n".join(perspectives)}, generate {num} more perspectives that are diverse but follow the sentiment type {typea} and Actual Perspectives."

   # API call to generate responses
   response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
         {"role": "system", "content": 'You are a simple diverse perspective generator who fulfills the instruction following the example.'},
         {"role": "user", "content": system_prompt}
         ],
      max_tokens=500,
   )
   return list(map(clean_text, [elem for elem in response.choices[0].message.content.split("\n") if elem.strip()]))

def fill_response_data(claim_type_dict):
   updated_claim_type_dict = {}
   type_map = {'UNDERMINE':'SUPPORT', 'SUPPORT':'UNDERMINE'}
   with ThreadPoolExecutor(max_workers=10) as executor:
      futures = {executor.submit(generate_response, claim, typea, type_map[typea], perspectives): (claim, type_map[typea]) for claim, r1 in claim_type_dict.items() for typea, perspectives in r1.items()}
      for future in as_completed(futures):
         claim, typea = futures[future]
         updated_claim_type_dict.setdefault(claim, {})
         updated_claim_type_dict[claim].setdefault(typea, []).extend(future.result())
   return updated_claim_type_dict

def fill_response_data_mod(claim_type_dict):
   updated_claim_type_dict = {}
   with ThreadPoolExecutor(max_workers=10) as executor:
      futures = {executor.submit(generate_response_mod, claim, typea, r2['num'], r2['opinions']): (claim, typea) for claim, r1 in claim_type_dict.items() for typea, r2 in r1.items()}
      for future in as_completed(futures):
         claim, type = futures[future]
         updated_claim_type_dict.setdefault(claim, {})
         updated_claim_type_dict[claim].setdefault(type, []).extend(future.result())
   return updated_claim_type_dict

# len_det = get_avg_length(data)
# final_ret2 = fill_response_data_mod(len_det)

# for i in range(len(data)):
#    claim = data[i]['Claim']
#    if claim in final_ret2:
#       for subitem in data[i]['Perspectives']:
#          if subitem in final_ret2[claim]:
#             data[i]['Perspectives'][subitem]['opinions'].extend(final_ret2[claim][subitem])
# print("Data stores updated...\n")

# with open("perspectrum_balanced_NumMatch.jsonl", 'w', encoding='utf-8') as d:
#    for grp in data:
#       d.write(json.dumps(grp, ensure_ascii=False) + '\n')
# print("Final writing done.....\n")


ret_det = check_imbalance(data)
print("Selected Imbalance data....\n")
final_ret = fill_response_data(ret_det)

for i in range(len(data)):
   claim = data[i]['Claim']
   if claim in final_ret:
      for subitem in final_ret[claim]:
         data[i]['Perspectives'].setdefault(subitem, {})
         data[i]['Perspectives'][subitem]['opinions'] = list(map(clean_text, final_ret[claim][subitem]))
print("Data stores updated...\n")

with open("perspectrum_balanced_final.jsonl", 'w', encoding='utf-8') as d:
   for grp in data:
      d.write(json.dumps(grp, ensure_ascii=False) + '\n')
print("Final writing done.....\n")