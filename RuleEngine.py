import fitz  # PyMuPDF
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
    """
    do_rules = []
    dont_rules = []
    current_section = None

    for sentence in sentences:
        # Strip leading and trailing spaces for robustness
        sentence = sentence.strip()

        # Use regex to match "Do:" or "Don't:" after a dot, with optional spaces
        if sentence.startswith("Do:"):
            current_section = "do"
            do_rules.append(sentence.split("Do:", 1)[1].strip())  # Add the rule without "Do:"
        elif sentence.startswith("Don't:"):
            current_section = "dont"
            dont_rules.append(sentence.split("Don't:", 1)[1].strip())  # Add the rule without "Don't:"
        elif current_section == "do":
            do_rules[-1] += " " + sentence  # Append to the last "do" rule
        elif current_section == "dont":
            dont_rules[-1] += " " + sentence  # Append to the last "dont" rule

    rules = {
        "do": do_rules,
        "dont": dont_rules
    }
    return rules"""
   
    rules = []
    for sentence in sentences:
      doc = nlp(sentence)
      rule = {}
    
    # Identify verb and its children (potential subjects and objects)
      verb = None
      for token in doc:
       if token.pos_ == "VERB":
        verb = token
        break  # Exit loop after finding the first verb
    
       if verb:
      # Analyze children of the verb to find the subject
         for child in verb.children:
          if child.dep_ in ("nsubj", "nsubjpass"):  # Common subject dependencies
           rule["target"] = child.text
           break  # Stop after finding the first subject
      
      # Update consequence based on sentiment
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
        if rule:  # Add more conditions to verify the content if needed
            verified_rules["do"].append(rule)
    
    for rule in rules["dont"]:
        if rule:  # Add more conditions to verify the content if needed
            verified_rules["dont"].append(rule)
    
    return verified_rules












