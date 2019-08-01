## About

Passive recon script integrating several tools:

- whois
- [sublist3r](https://github.com/aboul3la/Sublist3r)
- [shodan](https://www.shodan.io/)
- google scraping

## Setup

```
export SHODAN_API_KEY=xxx # find in shodan portal
export HUNTER_API_KEY=xxx # make a free account on hunter.io

brew install chromedriver
brew install Caskroom/versions/google-chrome-canary

pip install -r requirements.txt
```

## Running Passive Recon

Interactively Run in command line:

```
cd scripts
python recon.py
```

Launch Flask app:

```
python app.py
```

Visit 0.0.0.0/3000