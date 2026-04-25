# FRCWorldsTracker
Tracks specified teams at the FIRST Robotics Competition World Championship.

The `config.json` file will need to be updated every year. It will also need to be updated to match
whichever spreadsheet your Google Service Account has access to.

See here for how to create a google service account: https://knowledge.workspace.google.com/admin/users/create-a-service-account

You will need to populate the google_sheets/GServAcc file with your service account's credentials.
Then you will need to create a google sheet and share the sheet with your service account (editing permissions).

You will also need to populate the .tba_api_key file with your The Blue Alliance API key which can be obtained
for free with an account.

Running is simple:
`python main.py --teams 2056 1114 7558 4946 9785 1241 1325 4678 4476 5406 7712 610 1360 2702 11270 9098 10015`
(This example is for Ontario District teams competing at the World Championship in 2026).

Built for Python 3.13+.
