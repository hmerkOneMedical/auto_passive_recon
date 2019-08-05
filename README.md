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

Visit 0.0.0.0/3003

## Deployed to heroku + scaled up web and worker:

```
heroku ps:scale web=1
heroku ps:scale worker=1
```

### To deploy, ensure you have added backpacks to support selenium / chrome driver.

```
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-chromedriver
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
```

### Set up redis for background processes

```
heroku addons:create heroku-redis:hobby-dev --app auto-passive-recon
```

Alternatively, set a different REDIS_URL:

```
export REDIS_URL=xxx
```

To run redis locally, execute ./run-redis.sh
