# NSD Alumni Intelligence Pipeline

A production-ready Python pipeline for automatically collecting and structuring publicly available information about National School of Drama (NSD) graduates (2014–2019).

The system takes a list of NSD alumni names and graduation years, searches the internet, extracts relevant information using a local LLM via Ollama, and generates a structured database.

---

## Features

### Input Support
- CSV input
- Excel (.xlsx) input

Expected columns:

| Name | Graduation Year |
|-------|----------------|
| Amanpreet Kaur | 2014 |
| Chirag Garg | 2014 |

---

## Information Collected

### Basic Information
- Full name
- Alternative names
- Graduation year
- Current profession
- Current organization
- Current city/location

### Online Presence
- Personal website
- Portfolio website
- LinkedIn
- Instagram
- Facebook
- YouTube
- IMDb
- Twitter/X
- Other public profiles

### Theatre Information
- Plays acted in
- Plays directed
- Plays written
- Theatre groups
- Theatre companies
- Repertory associations
- Film appearances
- TV appearances
- Workshops conducted
- Awards

### Public Contact Information
Only publicly available information is collected:

- Public phone numbers
- Public email addresses
- Public contact pages
- Management contacts

---

## Ethical Constraints

This project intentionally avoids:

- Guessing phone numbers
- Guessing email addresses
- Inferring personal information
- Accessing private content
- Bypassing logins
- Circumventing website restrictions
- Collecting non-public data

---

## Search Sources

The pipeline searches across multiple publicly available sources:

- Google/DuckDuckGo
- LinkedIn
- Instagram
- Facebook pages
- IMDb
- Theatre websites
- Festival websites
- News articles
- YouTube interviews
- Portfolio websites
- Personal websites
- NSD pages
- Repertory companies
- Medium articles
- Public PDFs
- Wikipedia

---

## Project Structure

```text
project_root/
│
├── input/
│   └── nsd_graduates.xlsx
│
├── output/
│   ├── alumni_data.csv
│   ├── alumni_data.xlsx
│   └── alumni_data.json
│
├── cache/
│
├── logs/
│
├── models/
│
├── main.py
├── search.py
├── extractor.py
├── llm_parser.py
├── utils.py
├── requirements.txt
│
└── README.md
```

---

## System Architecture

```text
Input CSV/Excel
        ↓
Generate contextual search queries
        ↓
Collect search results
        ↓
Extract webpage text
        ↓
Send data to local LLM
        ↓
Parse structured JSON
        ↓
Confidence filtering
        ↓
Deduplication
        ↓
Output generation
```

---

## LLM Configuration

This project uses a local LLM through Ollama.

Default:

```bash
gemma3
```

Fallback:

```bash
llama3:8b
```

Install Ollama:

https://ollama.com/download

Pull model:

```bash
ollama pull gemma3
```

or

```bash
ollama pull llama3:8b
```

Test:

```bash
ollama run gemma3
```

---

## Installation

Clone repository:

```bash
git clone https://github.com/yourusername/nsd-alumni-intelligence.git

cd nsd-alumni-intelligence
```

Create virtual environment:

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

Linux/Mac:

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Example requirements.txt

```text
pandas
openpyxl
requests
beautifulsoup4
duckduckgo-search
ollama
tqdm
retry
loguru
rapidfuzz
lxml
```

---

## Input Format

Place your Excel or CSV file inside:

```text
input/
```

Example:

```csv
Name,Graduation Year
Amanpreet Kaur,2014
Chirag Garg,2014
Jayanta Narzary,2014
```

---

## Running the Project

Run:

```bash
python main.py
```

The pipeline will:

1. Read names
2. Generate contextual search queries
3. Search the web
4. Download webpage content
5. Extract structured information
6. Run local LLM analysis
7. Generate final outputs

---

## Output

Generated files:

```text
output/
├── alumni_data.csv
├── alumni_data.xlsx
└── alumni_data.json
```

Example output:

```json
{
  "name":"Amanpreet Kaur",
  "graduation_year":"2014",
  "current_profession":"Actor",
  "current_location":"Mumbai",
  "website":null,
  "portfolio":null,
  "linkedin":"...",
  "instagram":"...",
  "plays_acted_in":[
      "Play A",
      "Play B"
  ],
  "plays_directed":[
      "Play C"
  ],
  "public_emails":[
      "contact@example.com"
  ],
  "sources":[
      "https://..."
  ]
}
```

---

## Robustness Features

### Reliability

- Retry handling
- Request timeouts
- Network failure handling
- Logging

### Data Quality

- Duplicate detection
- Ambiguous name handling
- Confidence scoring
- Low-confidence filtering
- Structured JSON validation

### Performance

- Caching
- Rate limiting
- Reduced duplicate searches

---

## Logs

Logs are stored in:

```text
logs/
```

Example:

```text
2026-05-26 18:20:41 INFO Searching: Amanpreet Kaur NSD
2026-05-26 18:20:44 INFO Parsing results
2026-05-26 18:20:48 INFO Confidence Score: 0.91
```

---

## Running in VS Code

Open folder:

```bash
code .
```

Select interpreter:

```text
Ctrl + Shift + P
Python: Select Interpreter
```

Choose:

```text
venv
```

Run:

```bash
python main.py
```

---

## Future Improvements

- Parallel processing
- GPU acceleration
- Vector database integration
- RAG-based retrieval
- Semantic duplicate detection
- Theatre-specific source prioritization
- Dashboard interface

---

## Disclaimer

This tool only collects publicly available information.

Users are responsible for complying with website terms of service, privacy laws, and ethical data usage practices.

---

## License

MIT License
