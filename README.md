The goal of this app is to find more vendors in less time.

<b>How it works</b> <br>
Send a slack message on #automation-vendor-search
It will trigger a google search, and fetch the top 10 results
It will look at every result website, and scrape several pages on this website for email addresses 
It will retrieve one or more contact per url and send that back on slack
The whole process generally takes less than a minute

<b>Notes</b><br>
You can increase the # URLs looked at in Zapier, but it tends to time out
Some websites are blacklisted: eventbrite, facebook, etc. 
To investigate errors:
Look at the zap run that errored
For all details, look at the app logs 
We only have 100 Google Searches per day. I’m not sure how to increase that or how much that’d cost. Right now, it’s free

<b>Things to improve</b><br>
Email format is not perfect. Emails are often concatenated with phone numbers - requires manual cleaning before using
The app needs to be booted every day. For the app to be always accessible, we would need to use Docker, which I am yet to learn. 
Break down the App in 2 steps in order to improve user experience and increase # URLs per request:
1. Fetch URLs and send them back on slack
2. Scrape Emails 
Use a Slack Bot instead of messages detected by zapier
We don't need an actual server on EC2. There must be a way to run the app serverless with Lambda 
In the future, this app could be in real time every time a customer requests an experience for which we don’t already have a vendor.

<b>Useful queries</b><br>
SSH into EC2 from app folder
ssh -i vendor-search-key.pem ec2-user@{server IP}
Then run the app: python3 app.py
Send test API request from CLI (to test): 
curl -X POST http://{server IP}/trigger_search -H "Content-Type: application/json" -d "{\"query\": \"nyc candle making workshop\", \"num_results\": 5}"

<b>Useful links</b><br>
Check Google API usage: https://console.cloud.google.com/apis/api/customsearch.googleapis.com
Check AWS EC2 usage: https://us-west-2.console.aws.amazon.com/ec2/home

