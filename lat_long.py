import os, urllib, string, fileinput, sys
from xml.dom import minidom

"""
Example source file format:

id|venue_code|name|address1|city|state|postalcode|country
3394|70A|Arrowhead Stadium|1 Arrowhead Dr.|Kansas city|MO|64129|US
884|V06|Justin Herman Plaza|1 MARKET ST|San francisco|CA|94105|US
77|ARC|Arco Arena|1 Sports Parkway|Sacramento|CA|95834|US
2902|TOK|Tokyo Dome|1-3-61 Koraku Bunkyo-Ku|Tokyo||112|JP
"""

source = 'venues.txt'
target = 'latlng.txt'

def processfile(name):
    """ 
    Parse address data from source file
    Generate API requests
    Write updates to include lat/lng values
    """
    records = []
    for line in fileinput.input(name):
        if fileinput.isfirstline():
            columns = line.split('|')

        if not fileinput.isfirstline():
            try:
                line[1]
                # Strip out characters that could cause errors on API request
                line = line.replace('\n', '').replace(".", "")
                line = line.replace(" ", "+").replace("&", "and")
                address = line.split('|')
                # In my case, I needed the venue name in its original form for
                # inclusion in the UPDATE, so I'm returning spaces to field 3
                address[2] = address[2].replace("+", " ")
                # Rebuild each address
                newaddress = []
                newaddress.append(address[3])
                newaddress.append(address[4])
                newaddress.append(address[5])
                newaddress.append(address[6])
                newaddress.append(address[7])
                newaddress.append(address[2])
                # Then append each address back to a new record set
                records.append(newaddress)
            except IndexError:
                print "emptyline"

    requesturl = 'http://maps.googleapis.com/maps/api/geocode/xml?address='
    for row in records:
        request = '%s%s,%s,%s,%s,%s&sensor=false' %(requesturl,row[0],row[1],
                    row[2],row[3],row[4])
        # Example: 
        # http://maps.googleapis.com/maps/api/geocode/xml?address=1+ \
        #        Arrowhead+Dr,Kansas+city,MO,64129,US&sensor=false

        # Parse the XML returned by the request
        dom = minidom.parse(urllib.urlopen(request))
        try:
            lat = dom.getElementsByTagName('lat')[0].firstChild.nodeValue
            lng = dom.getElementsByTagName('lng')[0].firstChild.nodeValue
            row[1] = row[1].replace("+", " ")
            update = ('UPDATE venues SET lat="%s", lng="%s" WHERE name="%s"' + 
                      'AND city="%s" AND country="%s";\n') %(lat,lng,row[5],
                      row[1],row[4])
        except IndexError:
            # If lat/lng values are not returned in the XML
            update = ('/* ZERO_RESULTS WHERE name="%s" AND city="%s" AND ' + 
                      'country="%s" */\n') %(row[5],row[1],row[4])
        with open(target, "a") as f:
            f.write(update)

    return records


def main():
    addresses = processfile(source)


if __name__ == "__main__":
    main()

