#!/bin/bash

# uncomment for debugging
#set -x

email="$(jq -r '.email' <config.json)"
token="$(jq -r '.token' <config.json)"
since="1 day ago"

email="$(python -c "import urllib;print urllib.quote(raw_input())" <<< "${email}")"

#activities=$(cat activityList.txt)
activities=$(curl "https://fitnesskeeperapi.com/RunKeeper/deviceApi/getActivityUUIDs?lastSyncTime=$(($(date -d "${since}" +"%s") * 1000))&maxWorkoutPaceVersion=2&utcOffsetSec=-25200&apiVer=2.3&timeZoneStr=America%2FLos_Angeles&deviceApp=paid%2C9.11.1.6494&device=android%2Csdk_gphone_x86%2C8.0.0%2C26%2CAndroid+SDK+built+for+x86&deviceID=e61a5b07-3709-4d4e-8b0c-6ba42d7d7033&email=${email}&maxWorkoutUnitsVersion=0" -H "authorization: Bearer ${token}" | jq -r '.cardioActivities.addedOrModifiedActivityIds[] | .uuid')

for activity in $activities; do
  echo $activity
  curl "https://fitnesskeeperapi.com/RunKeeper/deviceApi/activities?maxWorkoutPaceVersion=2&utcOffsetSec=-25200&apiVer=2.3&timeZoneStr=America%2FLos_Angeles&deviceApp=paid%2C9.11.1.6494&device=android%2Csdk_gphone_x86%2C8.0.0%2C26%2CAndroid+SDK+built+for+x86&deviceID=e61a5b07-3709-4d4e-8b0c-6ba42d7d7033&email=${email}&maxWorkoutUnitsVersion=0" -H "authorization: Bearer ${token}" -d "includePoints=true&cardioActivities=%5B%22${activity}%22%5D&includeStatusUpdates=true" > rk/${activity}.json
  ./rk_to_gpx.py "rk/${activity}.json" # || exit
done
