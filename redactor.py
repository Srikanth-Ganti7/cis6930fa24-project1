import argparse
import os
import re
import sys
import spacy
from glob import glob
from nltk.corpus import wordnet
import nltk



def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, action='append')
    parser.add_argument('--output', required=True)
    parser.add_argument('--names', action='store_true')
    parser.add_argument('--dates', action='store_true')
    parser.add_argument('--phones', action='store_true')
    parser.add_argument('--address', action='store_true' )
    parser.add_argument('--concept', action='append' )
    parser.add_argument('--stats', required=True  )
    return parser.parse_args()


def load_spacy_model():
    nlp = spacy.load('en_core_web_md')
    return nlp

nltk.download('wordnet')
nltk.download('omw-1.4')

def get_synonyms(word):
    """ Get synonyms of a word using WordNet """
    synonym_set = set()
    synset_list = wordnet.synsets(word)
    synset_index = 0

    while synset_index < len(synset_list):
        synset = synset_list[synset_index]
        lemma_list = synset.lemmas()
        lemma_index = 0

        while lemma_index < len(lemma_list):
            lemma = lemma_list[lemma_index]
            synonym_set.add(lemma.name().lower())  # Adding the synonyms in lowercase
            lemma_index += 1

        synset_index += 1

    print(f"Synonyms for '{word}': {', '.join(synonym_set)}")  # Debugging output to show synonyms
    return synonym_set


def redact_addresses(text):
    nlp = load_spacy_model()
    # Enhanced regex to capture various address formats, including street names, numbers, and ZIP codes
    address_pattern = re.compile(
        r'\b\d{1,5}\s'                        # Street number (1-5 digits)
        r'(?:[A-Za-z]+\s?){1,6}'               # Street name (1 to 6 words)
        r'(?:St|Ave|Blvd|Rd|Lane|Dr|Ct|Way|Pl|Plaza|Pkwy|Square|Sq|Street|Avenue|Road|Circle)?'  # Optional street type
        r'(?:\d{5})(?:-\d{4})?\b'          # Optional ZIP code (5 digits, optional +4)
    )

    # Finding all matches for debugging purposes
    matches = address_pattern.findall(text)
    #print(f"Addresses found: {matches}")

    # Replace each matched address with the redaction character
    redacted_text = text
    for match in matches:
        # Replace each address found with a redacted version of the same length
        redacted_text = re.sub(re.escape(match), '█' * len(match), redacted_text)
    
    #print(f"Final redacted text after all replacements:\n{redacted_text}")  # Debugging
    doc = nlp(redacted_text)
    location_count = 0
    spacy_matches = []

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  # Redact locations such as cities, countries, landmarks
            spacy_matches.append(ent.text)
            location_count += 1
            # Use regex to replace the location with redaction character '█'
            redacted_text = re.sub(r'\b{}\b'.format(re.escape(ent.text)), '█' * len(ent.text), redacted_text)

    #print(f"Addresses found (SpaCy): {spacy_matches}")

    total_count = len(matches) + location_count

    return redacted_text, total_count







def redact_names(doc, redacted_addresses):
    redacted_text = doc.text  # Get the full text as a string
    name_count = 0  # Counter for the number of successful redactions
    emails_to_redact = []

    # Load the SpaCy NLP model
    nlp = load_spacy_model()

    # List to store identified entities for debugging purposes
    identified_entities = []

    # Create a SpaCy doc for the entire text
    doc = nlp(redacted_text)

    # Iterate over all entities to identify names
    for ent in doc.ents:
        # Add identified entity for debugging
        identified_entities.append((ent.text, ent.label_))

        # Only redact names (PERSON label) that are not addresses
        if ent.label_ == "PERSON" and ent.text.lower() != "email" and ent.text.lower() not in redacted_addresses:
            # Additional filtering to exclude address-like entities
            entity_text = ent.text.replace('\n', ' ').strip()

            # Create a regex pattern to redact the entity
            name_pattern = re.compile(re.escape(entity_text), re.IGNORECASE | re.MULTILINE)
            updated_text, replacements = name_pattern.subn(lambda match: '█' * len(match.group()), redacted_text)

            # Only update if there were successful replacements
            if replacements > 0:
                redacted_text = updated_text
                name_count += replacements

    # Debug: Print all identified entities with their labels
    #print(f"Identified entities by SpaCy: {identified_entities}")

    # Handle salutations like "Dear [Name]"
    salutation_pattern = re.compile(r'\b(?:Dear|Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+)\b')
    salutation_matches = salutation_pattern.findall(redacted_text)
    for match in salutation_matches:
        # Replace the name found after the salutation with redacted characters
        updated_text, replacements = re.subn(r'\b{}\b'.format(re.escape(match)), '█' * len(match), redacted_text)
        if replacements > 0:
            redacted_text = updated_text
            name_count += replacements

    # Identify and redact all email addresses in the text
    email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
    emails = email_pattern.findall(redacted_text)
    for email in emails:
        emails_to_redact.append(email)

    # Redact all identified emails
    for email in emails_to_redact:
        # Replace the exact email match with redaction characters
        updated_text, replacements = re.subn(re.escape(email), '█' * len(email), redacted_text)
        if replacements > 0:
            redacted_text = updated_text
            name_count += replacements

    # Return redacted text and the count of names plus emails redacted
    return redacted_text, name_count









def redact_dates(text):
    # Enhanced regex pattern to match various date formats comprehensively
    date_pattern = re.compile(
        r'\b('
        # Matches MM/DD/YYYY or DD/MM/YYYY (e.g., 11/10/2024 or 10/11/2024)
        r'\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?'
        # Matches DD Month YYYY or DD Month (e.g., 5th November 2024 or 5th November)
        r'|(?:\d{1,2}(?:th|rd|st|nd)?)\s(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{2,4})?'
        # Matches Month DD, YYYY or Month DDth (e.g., November 5th, or November 15, 2024)
        r'|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:th|rd|st|nd)?,?(?:\s*\d{2,4})?'
        # Matches abbreviated or full day of the week followed by a date (e.g., Tue, 11/01 or Tuesday, November 5th)
        r'|(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(?:\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:th|rd|st|nd)?,?(?:\s*\d{4})?)'
        # Matches DD MMM YYYY or DD MMM (e.g., 25 Oct 2024 or 25 Oct)
        r'|(?:\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:\s\d{2,4})?)'
        # Matches month-day without year (e.g., Dec 5th)
        r'|(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:th|rd|st|nd)?)'
        # Matches full dates with day of the week (e.g., Wed, 6 Feb 2002)
        r'|(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        r')\b',
        re.IGNORECASE
    )
    
    # Debugging to check which dates are being matched
    matches = date_pattern.findall(text)
    #print(f"Dates found: {matches}")

    # Replace matched dates with redacted characters
    redacted_text = date_pattern.sub(lambda x: '█' * len(x.group()), text)
    return redacted_text, len(matches)





def redact_phone_numbers(text):
    # Regex pattern to match various US phone number formats
    phone_pattern = re.compile(
        r'(?:(?:\+1\s?)?\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'
    )
    # Substitute redacted characters for matched phone numbers
    redacted_text = phone_pattern.sub(lambda x: '█' * len(x.group()), text)
    return redacted_text, len(phone_pattern.findall(text))




def redact_concept_sentences(text, concepts):
    sentences = re.split(r'(?<=[.!?])', text)  # Splitting text at full stops while keeping them
    redacted_sentences = []
    concept_count = 0

    # Collect all synonyms for each concept
    concept_synonyms = set()
    for concept in concepts:
        concept_synonyms.update(get_synonyms(concept))
        concept_synonyms.add(concept.lower())  # Include the original concept word as well

    for sentence in sentences:
        should_redact = False
        # Check if any of the concepts or their synonyms are in the sentence
        for synonym in concept_synonyms:
            if re.search(r'\b' + re.escape(synonym) + r'\b', sentence, re.IGNORECASE):
                should_redact = True
                break
        
        if should_redact:
            redacted_sentences.append('█' * len(sentence))
            concept_count += 1
        else:
            redacted_sentences.append(sentence)
    
    return ''.join(redacted_sentences), concept_count


def process_files(files, output_dir, args):
    nlp = load_spacy_model()
    stats = {}

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Start with the unredacted text
            redacted_text = text
            file_stats = {}

            # Redact addresses first (important to handle addresses before named entities)
            if args.address:
                redacted_text, address_count = redact_addresses(redacted_text)
                file_stats['ADDRESS'] = address_count

            # Update the redacted text with the latest version and pass it to Spacy
            if args.names:
                doc = nlp(redacted_text)  # Generate the SpaCy doc on the latest redacted text
                redacted_text, name_count = redact_names(doc, [])
                file_stats['PERSON'] = name_count

            # Redact dates (work on the updated text)
            if args.dates:
                redacted_text, date_count = redact_dates(redacted_text)
                file_stats['DATE'] = date_count

            # Redact phone numbers (work on the updated text)
            if args.phones:
                redacted_text, phone_count = redact_phone_numbers(redacted_text)
                file_stats['PHONE'] = phone_count

            # Redact concept sentences (work on the latest text)
            if args.concept:
                redacted_text, concept_count = redact_concept_sentences(redacted_text, args.concept)
                file_stats['CONCEPT'] = concept_count

            # Write the redacted content to the output file
            output_filename = os.path.splitext(os.path.basename(file))[0] + ".censored"
            output_file = os.path.join(output_dir, output_filename)

            # Print final redacted text before writing to file for confirmation
            #print(f"Writing final redacted text to {output_file}:\n{redacted_text}")

            with open(output_file, 'w', encoding='utf-8') as out:
                out.write(redacted_text)

            stats[file] = file_stats

        except Exception as e:
            print(f"Error processing file {file}: {e}", file=sys.stderr)

    return stats






def output_statistics(stats, stats_output, output_dir):
    if not stats:
        print("No statistics to output.")
        return

    stats_text = "Redaction Statistics:\n"
    for file, data in stats.items():
        stats_text += f"\nFile: {file}\n"
        for key, value in data.items():
            stats_text += f"  {key}: {value}\n"

    # Always print statistics to terminal
    print(stats_text)

    # If --stats is set to 'stderr', save to 'stats.txt' in the output folder
    if stats_output == 'stderr':
        stats_file = os.path.join(output_dir, 'stats.txt')
        with open(stats_file, 'w') as f:
            f.write(stats_text)
        print(f"Statistics also saved to {stats_file}")



def main():
    args = get_arguments()

    # Find all files matching the input patterns
    files = []
    for pattern in args.input:
        files.extend(glob(pattern))

    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Process the files
    stats = process_files(files, args.output, args)

    # Output statistics in the specified output directory
    output_statistics(stats, args.stats, args.output)


if __name__ == "__main__":
    main()