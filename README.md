## About

Passive recon script integrating several tools:

- whois
- [sublist3r](https://github.com/aboul3la/Sublist3r)
- [shodan](https://www.shodan.io/)
- google scraping

# Running Passive Recon

## Locally

### Setup

```
export SHODAN_API_KEY=xxx # find in shodan portal
export HUNTER_API_KEY=xxx # make a free account on hunter.io

brew install chromedriver
brew install Caskroom/versions/google-chrome-canary

pip install -r requirements.txt
```

Interactively Run in command line:

```
cd scripts
python recon.py
```

Launch Flask app:

```
python app.py
```

Visit (http://127.0.0.1:5000/)[http://127.0.0.1:5000/]

## Deployed

### Setup

To deploy, ensure you have added backpacks to support selenium / chrome driver.

```
heroku login
heroku create app-name-here

heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-chromedriver
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome

heroku addons:create heroku-redis:hobby-dev --app app-name-here

git add .
git commit -m "fun message here"
git push heroku master

heroku ps:scale web=1
heroku ps:scale worker=1
```

### Alternative Options

If you prefer your own redis url, skip the addon step, and configure the REDIS_URL config variable.

```
heroku config:set REDIS_URL=xxx
```

To run redis locally, execute ./run-redis.sh
