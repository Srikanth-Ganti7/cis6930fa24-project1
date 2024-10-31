
# cis6930fa24 -- Project1

## Author

**Name**: Balasai Srikanth Ganti

**UFID** : 5251-6075

## Assignment Description 
This project creates a tool that automatically hides sensitive information in text documents. It can recognize and remove names, dates, addresses, phone numbers, and specific keywords. The tool uses advanced language processing techniques to identify these sensitive parts and replaces them with redacted text. The user can also define their own words or phrases to be redacted. The tool then saves the edited documents in a chosen location and provides a report on what was removed.


## How to install

To set up the environment, use pipenv to install the dependencies.

```bash
pipenv install .
```

## How to run
Run the program using the following commands:

### Redact information from files:
```bash
pipenv run python project1/redactor.py --input <input_files> --[options] --output <output_folder> --stats 'stderr'

```
To redact names, dates, addresses, phones, and concept "tax" from text files located in root and save them to output as <input_file_name>.confidential:
### Example:
```bash
pipenv run python redactor.py --input '*.txt' --names --address --dates --phones --concept 'tax' --output 'output/' --stats 'stderr'
```

The script will process the files, redact specified types of information, and save the results in the specified output directory. Redaction statistics will be displayed in the console and saved to stats.txt if --stats is set to stderr.

## Expected output

### stats output example

After running the program, each redacted file will be saved in the output directory with a .censored extension. Sample redaction statistics are displayed as follows:

```bash
Redaction Statistics:

File: sample.txt
  ADDRESS: 3
  PERSON: 5
  DATE: 2
  PHONE: 4
  CONCEPT: 1

Statistics also saved to output/stats.txt
```

### redacted output example:

From:   ████, █████████
> > Sent:   ████████████████████████ 7:52 AM
> > To:     ████, █████████; '████████████████████████'
> > Cc:     ████████████████████████; █████████████████████████
> > Subject:     RE: EPMI Draft Proposal

## Functions

#### redactor.py
- **get_arguments()**: Parses command-line arguments.
- **load_spacy_model()**: Loads the SpaCy model.
- **get_synonyms(word)**: Retrieves synonyms for a concept word using WordNet.
- **redact_addresses(text)**: Redacts addresses and general locations.
- **redact_names(doc, redacted_addresses)**: Redacts names, salutations, and email addresses.
- **redact_dates(text)**:  Redacts various date formats.
- **redact_phone_numbers(text)**: Redacts phone numbers.
- **redact_concept_sentences(text, concepts)**:Redacts sentences containing specified concept words.
- **process_files(files, output_dir, args)**: Processes files for redaction based on the selected options.
- **output_statistics(stats, stats_output, output_dir)**:Outputs redaction statistics to a file or terminal.

#### Libraries used
- **argparse**: For handling command-line arguments.
- **spacy**: For named entity recognition.
- **nltk**: Used for reading and extracting text from PDF files.
- **re**: For regular expressions.
- **re**: For regular expressions.
- **glob**: For handling file patterns.
- **os**: For file and directory management.


## Testcases

To ensure proper functionality, the following test cases are provided using pytest:


- **test_redact_addresses()**: Verifies accurate redaction of addresses.

- **test_redact_names()**: Checks name and email redaction.

- **test_redact_dates()**: Ensures accurate date redaction across formats.

- **test_redact_phone_numbers()**: Verifies phone number redaction.

- **test_redact_concept_sentences()**: Confirms redaction of concept-related sentences.


## How to run tests:
Make sure the following are installed in your environment:

1. **pipenv**: Used to manage the virtual environment.
2. **pytest**: Python testing framework.

To install all dependencies, run:

```bash
pipenv install

```

To run the testcases you go with the following command:

```bash
pipenv run python -m pytest -v
```



## Bugs and Assumptions:

1.  **Assumptions**: 

- The names in emails and Emails in general are redacted from the text, to ensure the purpose of hiding personal information is achieved.
- SpaCy - en_core_web_md is being used, and names, address identified by this model are only being identifeid and redacted. Although other larger models and alternatives are available, it was mentioned to use web_md model so went with the default.
-Synonyms are extracted from the web using "nltk" - wordnet; anything not identified by them are not being redacted.
- Extracted synonyms are taken from wordnet are printed in the terminal when the function is called, this helps maintain a record of possible synonyms for the "concept". Only those if available in the input text are redacted.
- Phone numbers are assumed to be 10 digits long, US standard format and no extensions are assumed.

2.  **Bugs**: 
- The redactor assumes message ID as Phone number too, As professor suggested it is better to over redact, and any message ID over 10 digits is partially redacted.
- Multi line Addresses and Addresses not in standard US format are a bit trick and partially redacted.
- Days are considered to be part of Dates format, sometimes is being partially redacted or rarely missed. Working hard on a fix for that. Observed it only once.





