import json
import random

with open('perspectrum_balanced_super_final.jsonl','r', encoding='utf-8') as p:
   data = p.readlines()

data = list(map(lambda x: json.loads(x), data))
print("Data Loaded...\n")

def generate_training_data(claim, context, support_opinions, undermine_opinions):
   training_examples = []

   total_opinions_count = len(support_opinions) + len(undermine_opinions)

   if total_opinions_count > 0:
      support_percentage = (len(support_opinions) / total_opinions_count) * 100
      undermine_percentage = (len(undermine_opinions) / total_opinions_count) * 100
   else:
      support_percentage = undermine_percentage = 0

   # Statistical summary instructions
   stats_prompts = [
      "What is the distribution of opinions about the following claim?",
      "Summarize the opinions about the following claim, including the number of positive and negative views.",
      "Compare the opinion distributions for the following claim."
   ]

   # Counts of different opinion types instructions
   count_prompts = [
      "How many supporting opinions are there about the following claim?",
      "How many undermining opinions are there about the following claim?"
   ]
   
   # Generate direct opinion instructions and answers
   training_examples.append({
      "Claim": claim,
      "Context": context,
      "Instruction": "What are the supporting opinions on the following claim?",
      "Answer": "\n".join([opinion.strip() for opinion in support_opinions]),
      "Polarity" : 1
   })
   
   training_examples.append({
      "Claim": claim,
      "Context": context,
      "Instruction": "What are the undermining opinions on the following claim?",
      "Answer": "\n".join([opinion.strip() for opinion in undermine_opinions]),
      "Polarity" : -1
   })

   chosen_stats_prompt = random.choice(stats_prompts)
   # Generate Statistics Prompt
   training_examples.append({
      "Claim": claim,
      "Context": context,
      "Instruction": chosen_stats_prompt,
      "Answer": f"Supporting: {support_percentage:.1f}%, Undermining: {undermine_percentage:.1f}%",
      "Polarity" : 1
   })

   chosen_count_prompt = random.choice(count_prompts)
   # Generate Count Prompt
   training_examples.append({
      "Claim": claim,
      "Context": context,
      "Instruction": chosen_count_prompt,
      "Answer": f"{len(support_opinions)} supporting opinions." if 'supporting' in chosen_count_prompt.lower() else f"{len(undermine_opinions)} undermining opinions.",
      "Polarity" : 1 if 'supporting' in chosen_count_prompt.lower() else -1
   })
   return training_examples

def generate_comprehensive_training_data(claim, context, support_opinions, undermine_opinions):
   # Ensure the answer is correctly formatted and complete
   if not support_opinions or not undermine_opinions:
      print("Partial", claim)

   training_examples = generate_training_data(claim, context, support_opinions, undermine_opinions)

   training_examples.append({
      "Claim": claim,
      "Context": context,
      "Instruction": "Analyze the following claim and provide all perspectives; ones that agree and ones that disagree.",
      "Answer": f"Supporting Perspectives:\n{'\n'.join([opinion.strip() for opinion in support_opinions])}\n\nUndermining Perspectives:\n{'\n'.join([opinion.strip() for opinion in undermine_opinions])}\n",
      "Polarity" : 1
   })
   
   return training_examples

Data_holder = {}
for dat in data:
   claim = dat["Claim"]
   sup_Pers = dat["Perspectives"]['SUPPORT']['opinions']
   und_Pers = dat["Perspectives"]['UNDERMINE']['opinions']
   context = f"Supporting Perspectives:\n{'\n'.join([f'- {opinion.strip()}' for opinion in sup_Pers])}\n\nUndermining Perspectives:\n{'\n'.join([f'- {opinion.strip()}' for opinion in und_Pers])}"
   Data_holder[claim] = generate_comprehensive_training_data(claim, context, sup_Pers, und_Pers)
print("Instruction Data Created")

with open("perspectrum_instruction_dataset.jsonl", 'w', encoding='utf-8') as d:
   for claim, data in Data_holder.items():
      for sub_data in data:
         d.write(json.dumps(sub_data, ensure_ascii=False) + '\n')
print("Final writing done.....\n")