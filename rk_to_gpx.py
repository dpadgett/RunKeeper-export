#!/usr/bin/python

import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
from datetime import timedelta
import pytz

file = 'activity.json'
if len(sys.argv) > 1:
  file = sys.argv[1]

base = 'base.gpx'
if len(sys.argv) > 2:
  base = sys.argv[2]

data = json.loads(open(file, 'r').read())
activity = data['cardioActivities'][0]

ET.register_namespace('','http://www.topografix.com/GPX/1/1')
ET.register_namespace('gpxtpx','http://www.garmin.com/xmlschemas/TrackPointExtension/v1')
out = ET.parse(base)

ns = {'d': 'http://www.topografix.com/GPX/1/1', 'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}

trk = out.find('d:trk', ns)

start = pytz.timezone('America/Los_Angeles').localize(datetime.utcfromtimestamp(activity['startTime'] / 1000))
#start = pytz.timezone('America/New_York').localize(datetime.utcfromtimestamp(activity['startTime'] / 1000))
#start = pytz.timezone('US/Hawaii').localize(datetime.utcfromtimestamp(activity['startTime'] / 1000))

#start += timedelta(hours=2)

trk.find('d:name', ns).text = 'Running %s' % (start.strftime('%m/%d/%y %I:%M %p'))
localstart = start
start = start.astimezone(pytz.UTC)
time = trk.find('d:time', ns)
if time is None:
  time = out.find('d:metadata', ns).find('d:time', ns)
time.text = start.strftime('%Y-%m-%dT%H:%M:%SZ')
trkseg = trk.find('d:trkseg', ns)

path = activity['path']

hrs = activity['heartRate']
find_hr = lambda time: ([hrs[0]] + [hr for hr in hrs if hr['t'] < time])[-1]['hr']

steps = activity['steps']
def find_cad(time):
  find_step = lambda time: ([steps[0]] + [step for step in steps if step['t'] < time])[-1]
  cur = find_step(time)
  prev = find_step(time - (20 * 1000))
  return (cur['s'] - prev['s']) * 60 * 1000 / max(1, (cur['t'] - prev['t'])) / 2

if len(steps) == 0:
  print 'No steps'
  exit()

trkpts = trkseg.findall('d:trkpt', ns)
if len(trkpts) == 0:
  for pt in path:
    trkpt = ET.SubElement(trkseg, 'trkpt')
    trkpt.set('lat', '%f' % (pt[2]))
    trkpt.set('lon', '%f' % (pt[3]))
    ele = ET.SubElement(trkpt, 'ele')
    ele.text = '%f' % (pt[4])
    time = ET.SubElement(trkpt, 'time')
    time.text = (start + timedelta(milliseconds = pt[0])).strftime('%Y-%m-%dT%H:%M:%SZ')
    extensions = ET.SubElement(trkpt, 'extensions')
    tpx = ET.SubElement(extensions, 'gpxtpx:TrackPointExtension')
    if len(hrs) > 0:
      hr = ET.SubElement(tpx, 'gpxtpx:hr')
      hr.text = '%d' % (find_hr(pt[0]))
    if len(steps) > 0:
      cad = ET.SubElement(tpx, 'gpxtpx:cad')
      cad.text = '%d' % (find_cad(pt[0]))
else:
  print 'Using existing track'
  for trkpt in trkpts:
    time = trkpt.find('d:time', ns)
    try:
      dt = pytz.utc.localize(datetime.strptime(time.text, "%Y-%m-%dT%H:%M:%SZ"))
    except:
      dt = pytz.utc.localize(datetime.strptime(time.text, "%Y-%m-%dT%H:%M:%S.000Z"))
    #dt += timedelta(hours=2)
    #time.text = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    offset = timedelta.total_seconds(dt - start) * 1000
    ex = trkpt.find('d:extensions', ns)
    if ex is None:
      ex = ET.SubElement(trkpt, 'extensions')
    tpx = ex.find('gpxtpx:TrackPointExtension', ns)
    if tpx is None:
      tpx = ET.SubElement(ex, 'gpxtpx:TrackPointExtension')
    hr = tpx.find('gpxtpx:hr', ns)
    if len(hrs) > 0 and hr == None:
      #print hr.text + ' : %d' % find_hr(offset)
      hr = ET.SubElement(tpx, 'gpxtpx:hr')
      hr.text = '%d' % (find_hr(offset))
    if len(steps) > 0:
      cad = ET.SubElement(tpx, 'gpxtpx:cad')
      cad.text = '%d' % (find_cad(offset))

#out.write(sys.stdout, xml_declaration=True)
#print ''

outfile = 'rk/%s.gpx' % (localstart.strftime('%Y-%m-%d_%H-%M-%S'))
print 'Writing %s' % outfile
out.write(open(outfile, 'w'), xml_declaration=True)
