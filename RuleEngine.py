import fitz  
import spacy
import pymongo
import re

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def preprocess_text(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

def extract_rules(sentences):


    rules = []
    for sentence in sentences:
      doc = nlp(sentence)
      rule = {}
    
   
      verb = None
      for token in doc:
       if token.pos_ == "VERB":
        verb = token
        break  
    
       if verb:
      
         for child in verb.children:
          if child.dep_ in ("nsubj", "nsubjpass"):  # Common subject dependencies
           rule["target"] = child.text
           break  # Stop after finding the first subject
      
     
      if any(token.dep_ == "neg" for token in doc):
        rule["consequence"] = "Don't " + verb.text
      else:
        rule["consequence"] = "Always " + verb.text
      
      rule["action"] = verb.text
    
    rules.append(rule)
  
    return rules


def store_rules_mongodb(rules):
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["shakilco"]
        collection = db["OrganizationalRules"]
        collection.insert_one(rules)
        print("Rules stored successfully in MongoDB")
    except Exception as e:
        print(f"Error storing rules in MongoDB: {str(e)}")

def verify_rules(rules):
    verified_rules = {"do": [], "dont": []}
    
    for rule in rules["do"]:
        if rule:  
            verified_rules["do"].append(rule)
    
    for rule in rules["dont"]:
        if rule: 
            verified_rules["dont"].append(rule)
    
    return verified_rules












