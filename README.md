# 🔍 CyberSearch - Aggregated Cyberspace Search Tool (v0.1)

**CyberSearch** is a lightweight command-line tool that aggregates results from cyberspace search engines.  
Currently supports multiple platforms including **ZoomEye**, **FOFA**, **Quake**, **Shodan**, **Hunter**, and **DayDayMap** (with varying levels of support).  
Supports batch search from TXT files and multiple output formats.  
Useful for security researchers, red teamers, and digital reconnaissance.

---

## ✅ Features

- API key management via `.env` or `.yaml`
- Multi-engine search support (ZoomEye, FOFA, Quake, Shodan, Hunter, DayDayMap)
- Flexible filters and custom output fields
- Multiple export formats (JSON, CSV, XML, XLSX, TXT)
- Batch search from file input
- Verbose debugging mode
- Multi-engine fallback system (coming soon)
- Unified search syntax across platforms
- Icon hash search support
- Intelligent result deduplication
---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Supports three configuration methods (in order of priority):

#### Method 1: Environment Variables (Recommended)

```bash
export ZOOMEYE_API_KEY="your_zoomeye_api_key"
export FOFA_API_KEY="your_fofa_api_key" 
export SHODAN_API_KEY="your_shodan_api_key"
export HUNTER_API_KEY="your_hunter_api_key"
export QUAKE_API_KEY="your_quake_api_key"
export DAYDAYMAP_API_KEY="your_daydaymap_api_key"
```

#### Option 2: YAML (`~/.Cybersearch/api_keys.yaml`)

```yaml
zoomeye: your_zoomeye_api_key
fofa: your_fofa_api_key
shodan: your_shodan_api_key
hunter: your_hunter_api_key
quake: your_quake_api_key
daydaymap: your_daydaymap_api_key
```
YAML config file is expected at `~/.Cybersearch/api_keys.yaml` by default. You may override this path in `config.py`.

---
#### Method 2: .env File

Create a `.env` file in the project root directory:

```env
ZOOMEYE_API_KEY=your_zoomeye_api_key
FOFA_API_KEY=your_fofa_api_key
SHODAN_API_KEY=your_shodan_api_key
HUNTER_API_KEY=your_hunter_api_key
QUAKE_API_KEY=your_quake_api_key
DAYDAYMAP_API_KEY=your_daydaymap_api_key
```


### 3. Run examples

#### Search all platforms (default)
```bash
python Cybersearch.py \
  --query 'app="Nginx" || app="Apache" || app="IIS"' \
  --limit 100 \
  --fields ip,port,domain,title,country \
  --engine zoomeye,fofa \
  --output results.xlsx \
  --verbose
```

---

## ⚙️ Configuration File Support

In addition to command-line arguments, CyberSearch supports setting parameters and filters through configuration files:

### Configuration File Example (`config_filters.yaml`)

## ⚙️ Command-Line Arguments

| Argument     | Description                                |
|--------------|--------------------------------------------|
| `--query`    | Search keyword (e.g. `title="Apache"`)     |
| `--limit`    | Max results to return (default: 10)        |
| `--engine`   | Search engine to use. Options: fofa, zoomeye, hunter, quake, shodan, daydaymap. Default: all (search all engines concurrently) |
| `--fields`     | Output fields, comma-separated             |
| `--verbose`  | Enable debug logging                       |
| `--input`    | Path to TXT file for batch search          |
| `--output`   | Output file path and format(default: `results.json`) |
| `--icon`     | Path to .ico file for icon hash search |
| `--config`   | Path to custom config file |
| `--show-fields` | Show available output fields for selected engine |





## 📤 Output 

| Format | Description |
|--------|-------------|
| JSON | Structured data in JSON format |
| CSV | Comma-separated values |
| XML | Extensible Markup Language format |
| XLSX | Microsoft Excel spreadsheet |
| TXT | Plain text output |

Each output contains configurable fields like:
- IP address
- Port number 
- Domain name
- Title
- Country
- And more...

---

---

## 📁 Project Structure

```
cybersearch/
├── main.py               # CLI entry point
├── config.py             # API key loader
├── filters.py            # Field filtering
├── utils.py              # Utility functions
├── feed/
│   ├── zoomeye.py        # ZoomEye interface
│   ├── fofa.py           # FOFA support
│   ├── quake.py          # Quake support
│   ├── shodan.py         # Shodan support
│   ├── hunter.py         # Hunter support
│   └── daydaymap.py      # DayDayMap support 
├── .env                  # (ignored) for API key
├── api_keys.yaml         # (ignored) for API key
├── requirements.txt      # Dependencies
└── README.md             # This file
```

---

## 🔒 Safety Reminder

- DO NOT commit your `.env` or `api_keys.yaml` to GitHub
- Add them to `.gitignore` to protect sensitive data

---

## 🛣️ Roadmap

### ✅ v0.1 (Current)
- [x] Multi-platform API support (ZoomEye, FOFA, Quake, Shodan, Hunter, DayDayMap)
- [x] File export: JSON, CSV, XML, XLSX, TXT
- [x] Batch query from TXT input
- [x] Custom output fields via `--fields`
- [x] Verbose logging and debugging mode
- [x] Icon hash search (.ico file support)
- [x] Configuration file support with filtering
- [x] Pipeline input support (stdin)
- [x] Advanced result filtering (country, title, domain, port)

---

## 👨‍💻 Author

> Mengchen Wang ｜ Internship Project  
>  
> Feedback & PRs welcome 🙌

