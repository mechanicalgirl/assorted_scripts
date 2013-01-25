"""
This script pulls from the Sunlight Labs "openstates" API
to get information about legislators at the state level, 
do a count of their party affiliations, 
and return that information as 
1) a JSON object for visualizations
2) a table suitable for embed into an HTML page

Information about the specific API used can be found here:
http://python-sunlight.readthedocs.org/en/latest/services/openstates.html

To use the 'sunlight' library, you need to get an API key:
  http://services.sunlightlabs.com/

Then install the module:
  http://python-sunlight.readthedocs.org/en/latest/index.html
"""

import sunlight

import simplejson as json
import os.path
import re
import datetime

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

outfile = 'state_reps_list.txt'
uef = 'unemployment_figures.txt'

def find_state_reps():
  """
  Get a list of state legislators from all 50 states 
  and write a subset of that data to a dict.
  """
  statereps = {}
  f = os.path.exists(outfile)
  # If we've already got the list, just refer to that file
  # instead of hitting the API again.
  if f:
    # Get the file content and return it as the statereps dict
    f = open(outfile, 'r')
    statereps = eval(f.read())
    f.close()
  else:
    # Or hit the API, get the dict, and write it to a file
    for s in states:
      # legs = sunlight.openstates.legislators(state=s)
      legs = sunlight.openstates.legislators(state='TX')
      print legs
      # If you print 'legs', you'll see a dict with loads of
      # contact information for each state representative.
      # For my purposes, I'm only pulling out information 
      # about name and party affiliation.

      l = {}
      for leg in legs:
        name = leg['full_name']
        try:
          party = leg['party']
        except KeyError:
          party = None
        l[name] = party
      print s
      print l
      statereps[s] = l

    # At this point, the 'statereps' dict contains 
    # {'state':{'rep_name':'party_affiliation'}}
    # for each state.

    # Write the dict to a file so that data doesn't have to 
    # be pulled from the API again.
    f = open(outfile, 'w')
    f.write(str(statereps))
    f.close()

  return statereps


def converttojson(reps_dict):
  """
  Take a dict object and convert it to JSON
  """
  result = json.dumps(reps_dict, sort_keys=False, indent=4)
  return result


def partycount(reps_dict):
  """
  This method returns a summary count of party affiliations among 
  state legislators per state (e.g., state: dems=x, repubs=y, other=z)
  """
  partycount = {}
  for s in reps_dict:
    # Create lists to hold the party members on a per-state basis:
    demlist = []
    replist = []
    otherlist = []
    for k in reps_dict[s]:
      # print s, k, reps_dict[s][k]
      if reps_dict[s][k]:
        dem = re.search('Dem', reps_dict[s][k])
        rep = re.search('Repub', reps_dict[s][k])
        if dem:
          # print dem.group(0)
          # If the legislator's party affiliation contains the substring 'Dem',
          # add their name to the 'dem' list:
          demlist.append(k)
        elif rep:
          # If the legislator's party affiliation contains the substring 'Rep',
          # add their name to the 'rep' list:
          # print rep.group(0)
          replist.append(k)
        else:
          # If neither substring appears in the legislator's party affiliation, 
          # add their name to the 'other' list
          otherlist.append(k)
    c = {}
    # Get the length of each list and you have a count of 
    # dems vs. repubs vs. other for this state:
    c['Democrats'] = len(demlist)
    c['Republicans'] = len(replist)
    c['Other'] = len(otherlist)
    partycount[s] = c

  u = open(uef, 'r')
  unemployment = eval(u.read())
  u.close()
  ue_current = ''
  for ue in unemployment:
    ue_current = ue

  st_current = datetime.datetime.fromtimestamp(os.path.getmtime(outfile))

  # A bit ugly, but this creates an HTML table out of the count data
  # and writes it to a file - it could just as easily be output as 
  # a template context object, or printed to the shell.
  output = "<html><body>"
  output += "<p>State legislative data current as of %s</p>" % (st_current)
  output += "<p>Unemployment data current as of %s (source: US Department of Labor, Bureau of Labor Statistics)</p>" % (ue_current)
  output += "<table cellspacing='10'>\n"
  output += "<tr><td><b>STATE</b></td><td><b>Republicans</b></td> \
             <td><b>Other</b></td><td><b>Democrats</b></td> \
             <td>percent</td><td><b>Unemployment</b></td></tr>"

  # Let's sort the keys while we're at it, so the HTML shows the 
  # states in alphabetical order:
  for key in sorted(partycount.iterkeys()):
    output += "<tr><td align='center'>%s</td>" % (key)

    # calculate the percentage of Republican reps in each state
    percentlist = []
    for k in partycount[key]:
      output += "<td align='center'>%s</td>" % (partycount[key][k])
      percentlist.append(partycount[key][k])
    psum = float(percentlist[0]+percentlist[1]+percentlist[2])
    percent = "{0:.0f}%".format(float(percentlist[0])/psum * 100)
    output += "<td>%s</td>" % (percent)

    for ue in unemployment:
      for st in unemployment[ue]:
        if st == key:
          output += "<td align='center'>%s%%</td>" % (float(unemployment[ue][st]))

    output += "</tr>\n"
  output += "</table></body></html>"
  f = open('redvblue.html', 'w')
  f.write(str(output))
  f.close()

  return partycount

def main():
  # Get the initial dict of states, their legislators, 
  # and those legislators party affiliations:
  x = find_state_reps()
  y = converttojson(x) # Optional: convert the original dict to JSON

  # Get a count of party affiliations per state:
  z = partycount(x)
  # Convert that count data to a JSON object:
  pcount = converttojson(z)

if __name__ == '__main__':
  main()

# Some resources for doing visualizations with the resulting JSON object:
# json.bloople.net
# http://chris.photobooks.com/json/default.htm
# http://visualizer.json2html.com/

# Things I might want to add:
# 1) get the labor statistics by scraping this page instead of hardcoding:
#    http://www.bls.gov/web/laus/laumstrk.htm

# file:///Users/barbara/Code/sunlightlabs/redvblue/redvblue.html
