# 🔍 CyberSearch - Aggregated Cyberspace Search Tool (v0.1)

**CyberSearch** is a lightweight command-line tool that aggregates results from cyberspace search engines.  
Currently supports multiple platforms including **ZoomEye**, **FOFA**, **Quake**, **Shodan**, **Hunter**, and **DayDayMap** (with varying levels of support).  
Useful for security researchers, red teamers, and digital reconnaissance.

---

## ✅ Features

- API key management via `.env` or `.yaml`
- ZoomEye search support (`title`, `ip`, `domain`, `body`)
- Flexible filters (country, domain)
- Custom output fields via `--fields`
- Verbose mode for debugging
- Designed for multi-engine fallback (coming soon)

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt


```bash
pip install -r requirements.txt
```

### 2. Configure API keys

You can choose either of the following:

#### Option 1: `.env`

```
ZOOMEYE_API_KEY=your_zoomeye_api_key
```

#### Option 2: YAML (`~/.cybersearch/api_keys.yaml`)

```yaml
zoomeye: your_zoomeye_api_key
fofa:
  email: your_email@example.com
  key: your_fofa_api_key
```
YAML config file is expected at `~/.cybersearch/api_keys.yaml` by default. You may override this path in `config.py`.

---

### 3. Run example

```bash
python Cybersearch.py \
  --query 'title="Apache"' \
  --limit 5 \
  --fields ip,port,domain \
  --verbose
```

---

## ⚙️ Command-Line Arguments

| Argument     | Description                                |
|--------------|--------------------------------------------|
| `--query`    | Search keyword (e.g. `title="Apache"`)       |
| `--limit`    | Max results to return (default: 10)        |
| `--fields`   | Output fields, comma-separated             |
| `--country`  | Country filter (e.g. `CN`)                 |
| `--domain`   | Domain filter (e.g. `example.com`)         |
| `--verbose`  | Enable debug logging                       |

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

- [x] ZoomEye support
- [x] FOFA support
- [x] Quake support
- [x] Shodan support
- [x] Hunter support
- [x] DayDayMap support
- [ ] JSON export / file output
- [ ] Multi-engine fallback (automatic)

---

## 👨‍💻 Author

> Mengchen Wang ｜ Internship Project  
>  
> Feedback & PRs welcome 🙌
```
