
def add_header(kml_file):

    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml_file.write("<Document>\n")
    kml_file.write('<Style id="yellowPoly">\n')
    kml_file.write("<LineStyle>\n")
    kml_file.write("<color>Af00ffff</color>\n")
    kml_file.write("<width>6</width>\n")
    kml_file.write("</LineStyle>\n")
    kml_file.write("<PolyStyle>\n")
    kml_file.write("<color>7f00ff00</color>\n")
    kml_file.write("</PolyStyle>\n")
    kml_file.write("</Style>\n")
    kml_file.write("<Placemark><styleUrl>#yellowPoly</styleUrl>\n")
    kml_file.write("<LineString>\n")
    kml_file.write("<Description>Speed in MPH, not altitude.</Description>\n")
    kml_file.write("<extrude>1</extrude>\n")
    kml_file.write("<tesselate>1</tesselate>\n")
    kml_file.write("<altitudeMode>absolute</altitudeMode>\n")
    kml_file.write("<coordinates>\n")

def convert_to_mins(coordinate):

    converted_val = int(coordinate/100) + (coordinate - (int(coordinate/100) * 100)) / 60
    return str(converted_val)

def add_coordinates_to_body(kml_file, data_frame):

    for row in data_frame.iterrows():
        latitude = convert_to_mins((list(row[1]))[3])
        longitude = convert_to_mins((list(row[1]))[5])
        kml_file.write('-' + longitude+ ',' + latitude + ',' + str(0) + '\n')

def add_red_placemark_for_stops(list_of_stops, kml_file):


    for longitude, latitude in list_of_stops:
        longitude = convert_to_mins(longitude)
        latitude = convert_to_mins(latitude)
        kml_file.write("<Placemark>\n")
        kml_file.write("<description>Red PIN for A Stop</description>\n")
        kml_file.write('<Style id="normalPlacemark">\n')
        kml_file.write("<IconStyle>\n")
        kml_file.write("<color>ff0000ff</color>\n")
        kml_file.write("<Icon>\n")
        kml_file.write("<href>http://www.clker.com/cliparts/0/U/T/f/f/m/mappinyellow-md.png</href>\n")
        kml_file.write("</Icon>\n")
        kml_file.write("</IconStyle>\n")
        kml_file.write("</Style>\n")
        kml_file.write("<Point>\n")
        kml_file.write('<coordinates>-' + longitude + ',' + latitude + ',0</coordinates>\n')
        kml_file.write("</Point>\n")
        kml_file.write("</Placemark>\n")


def add_red_placemark_for_left_turns(list_of_left_turns, kml_file):

    for longitude, latitude in list_of_left_turns:
        longitude = convert_to_mins(longitude)
        latitude = convert_to_mins(latitude)
        kml_file.write("<Placemark>\n")
        kml_file.write("<description>Red PIN for A Left Turn</description>\n")
        kml_file.write('<Style id="normalPlacemark">\n')
        kml_file.write("<IconStyle>\n")
        kml_file.write("<color>00ff00</color>\n")
        kml_file.write("<Icon>\n")
        kml_file.write("<href>http://www.clker.com/cliparts/0/U/T/f/f/m/mappinyellow-md.png</href>\n")
        kml_file.write("</Icon>\n")
        kml_file.write("</IconStyle>\n")
        kml_file.write("</Style>\n")
        kml_file.write("<Point>\n")
        kml_file.write('<coordinates>-' + longitude + ',' + latitude + ',0</coordinates>\n')
        kml_file.write("</Point>\n")
        kml_file.write("</Placemark>\n")


def add_body(kml_file, data_frame, list_of_stops, list_of_left_turns):

    add_coordinates_to_body(kml_file, data_frame)

    # Tags after adding coordinates
    kml_file.write("</coordinates>\n")
    kml_file.write("</LineString>\n")
    kml_file.write("</Placemark>\n")

    # Adds red placemarks where vehicle was stopped
    add_red_placemark_for_stops(list_of_stops, kml_file)

    # Adds green placemarks where vehicle took a left turn
    add_red_placemark_for_left_turns(list_of_left_turns, kml_file)


def add_trailer(kml_file):

    kml_file.write(" </Document>\n")
    kml_file.write("</kml>\n")


def convert_GPS_to_KML(data_frame, list_of_stops, list_of_left_turns):

    kml_file = open('kml_file.kml', 'w')

    add_header(kml_file)
    add_body(kml_file, data_frame, list_of_stops, list_of_left_turns)
    add_trailer(kml_file)