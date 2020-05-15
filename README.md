# RunKeeper Exporter (with cadence!)

This project lets you export your RunKeeper tracks to .gpx, including run cadence.
(The RunKeeper website has a built in function to do this export, but it does not include cadence.)

To use, you will need to fill in the config.json with your credentials: your RunKeeper email address, and an authorization token.
In order to get the authorization token, I used the following steps:

1. Download and install Android Studio.
2. Create and launch a virtual Android device (do not use an image with Google Play installed, as you cannot root it).
3. Download and install mitmproxy.
4. Configure the emulator to accept the mitmproxy certificate as a system cert (see https://docs.mitmproxy.org/stable/howto-install-system-trusted-ca-android/)
5. Download and install the RunKeeper .apk onto your emulator.  (It is available at for example https://apkpure.com/runkeeper-gps-track-run-walk/com.fitnesskeeper.runkeeper.pro)
6. Launch the app and log in.
7. Inspect in mitmproxy a request going out to https://fitnesskeeperapi.com/RunKeeper/deviceApi and check the request headers for Authorization: Bearer.  It will contain the authentication token necessary.

Note: it seems the token doesn't expire.  But if it does, just reauthenticate in the emulator and extract the new token.

Once config.json is set up, you can just run ./fetch_rk_activities.sh to download the past 1 day's worth of activities (configurable in the script).  It will generate a .gpx file for any activity found to include cadence data.

One thing I find useful is that the RunKeeper data is not very fine grained.  Other apps such as Wahoo Fitness export data every 1 second, but do not record cadence.
To solve that, I usually record in both apps.  Once the Wahoo track is saved, I convert it to .gpx using Garmin Connect, and then I can just merge in the cadence data
from RunKeeper to the existing Wahoo .gpx track using i.e.:

./rk_to_gpx.py rk/1e44794d-aef7-4d21-aa42-a199fdbb875a.json rk/activity_4907706349.gpx

and upload the resulting merged file to Strava.