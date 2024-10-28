import argparse
import os
import re
import sys
import spacy
from glob import glob
from nltk.corpus import wordnet
import nltk


def get_arguments():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files")
    parser.add_argument('--input', required=True, action='append', help="Input file(s), supports glob patterns")
    parser.add_argument('--output', required=True, help="Directory to store redacted files")
    parser.add_argument('--names', action='store_true', help="Redact names")
    parser.add_argument('--dates', action='store_true', help="Redact dates")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers")
    parser.add_argument('--address', action='store_true', help="Redact addresses")
    parser.add_argument('--concept', action='append', help="Redact sentences related to concept(s)")
    parser.add_argument('--stats', required=True, help="Output statistics (stderr, stdout, or file)")
    return parser.parse_args()


def load_spacy_model():
    nlp = spacy.load('en_core_web_sm')
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
    print(f"Addresses found: {matches}")

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

    print(f"Addresses found (SpaCy): {spacy_matches}")

    total_count = len(matches) + location_count

    return redacted_text, total_count











def redact_names(doc, redacted_addresses):
    redacted_text = doc.text  # Get the full text as a string
    name_count = 0  # Counter for the number of redactions

    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.text not in redacted_addresses:  # Only redact names, not addresses
            name_count += 1
            # Use regex to replace the name with redaction character '█'
            redacted_text = re.sub(r'\b{}\b'.format(re.escape(ent.text)), '█' * len(ent.text), redacted_text)

    return redacted_text, name_count  # Return redacted text and count of names redacted




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
    phone_pattern = re.compile(r'\(?\b[2-9][0-9]{2}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b')
    redacted_text = phone_pattern.sub(lambda x: '█' * len(x.group()), text)
    return redacted_text, len(phone_pattern.findall(text))


def redact_concept_sentences(text, concepts):
    sentences = re.split(r'(?<=[.!?])', text)  # Splitting text at full stops while keeping them
    redacted_sentences = []

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
        else:
            redacted_sentences.append(sentence)
    
    return ''.join(redacted_sentences)


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
                redacted_text = redact_concept_sentences(redacted_text, args.concept)

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






def output_statistics(stats, stats_output):
    if not stats:
        print("No statistics to output.")
        return
    
    stats_text = "Redaction Statistics:\n"
    for file, data in stats.items():
        stats_text += f"\nFile: {file}\n"
        for key, value in data.items():
            stats_text += f"  {key}: {value}\n"

    if stats_output == 'stderr':
        print(stats_text, file=sys.stderr)
    elif stats_output == 'stdout':
        print(stats_text)
    else:
        with open(stats_output, 'w') as f:
            f.write(stats_text)


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

    # Output statistics
    output_statistics(stats, args.stats)


if __name__ == "__main__":
    main()
