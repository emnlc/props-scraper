# props-scraper

Python Selenium player props scraper for sportsgrid.com

# Setup

## Docker

To run this scraper using Docker, run these two commands:

```
docker build -t props-scraper .
```

```
docker run -d -p 8080:8080 props-scraper
```

The endpoint will now be available at: `http://localhost:8080/api/nba/stats`

## Locally

To run this scraper locally, run these commands:

```
pip install -r requirements.txt
```

#### Windows
```
python app.py
```

#### Mac / Linux

```
python3 app.py
```

The endpoint will be available at: `http://127.0.0.1:8080`