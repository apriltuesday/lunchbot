# Lunchbot

Lunchbot wants to know what's for lunch.

Adapted from [importio-slack-app](https://github.com/apriltuesday/importio-slack-app) for the Slack Events API.

## Setup

You'll need a Slack app subscribed to the `app_mention` event, and you'll need your OAuth token
and signing secret to run the app. For help setting this up, check Slack documentation.

```bash
pip install -r requirements.txt
export SLACK_BOT_TOKEN=<token>
export SLACK_SIGNING_SECRET=<secret>
python bot.py
```

This will run the bot locally on port 3000.

## To-Do
* Cache menu files
* Support [DMs](https://api.slack.com/events/message.im)
* Slightly future proof - e.g. make it easy to write new "menu providers"
