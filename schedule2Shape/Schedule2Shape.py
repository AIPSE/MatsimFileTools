import xml.etree.ElementTree as ET
from shapely.geometry import LineString, Point

# Hardcode paths to xml files
# from schedule2Shape import Shapely2ESRI
from Shapely2ESRI import Shapely2ESRI

networkfilepath = "C:\\Users\\lachlan\\Documents\\hell\\matsim_network_2016_w-pt.xml"
schedulefilepath = "C:\\Users\\lachlan\\Documents\\hell\\outputScheduleFile.xml"
outfilepath = "C:\\Users\\lachlan\\Documents\\hell\\transitShapeFile.shp"
projectionfilepath = "C:\\Users\\lachlan\\Documents\\hell\\epsg3879.prj"

print("network path is " + networkfilepath)
print("schedule path is " + schedulefilepath)
print("output file path is " + outfilepath)
print("projection file path is " + projectionfilepath)

# open network file and parse and store nodes
tree = ET.parse(networkfilepath)
root = tree.getroot()
nodesRoot = tree.find("nodes")
allNodes = {}
for node in nodesRoot.findall('node'):
    id = node.get('id')
    x = node.get('x')
    y = node.get('y')
    newNode = {'id': id, 'x': x, 'y': y}
    allNodes[id] = newNode

print("parsed and stored nodes")
linksRoot = tree.find("links")
allLinks = {}
for link in linksRoot.findall('link'):
    id = link.get('id')
    nfrom = link.get('from')
    nto = link.get('to')
    newLink = {'id': id, 'from': nfrom, 'to': nto}
    allLinks[id] = newLink
print("parsed and stored links")
# open schedule file and build something

tree = ET.parse(schedulefilepath)
root = tree.getroot()

# allLines
allRoutes = {}
# allRoutes = []
for line in root.findall('transitLine'):
    tlID = line.get('id')
    for transitRoute in line.findall('transitRoute'):
        trID = transitRoute.get('id')
        # print(trID)
        route = transitRoute.find('route')
        points = []
        if route is None:
            print("no route found")
        for link in route.findall('link'):
            refID = link.get('refId')
            # get the link info
            thelink = allLinks[refID]
            if thelink is None:
                print("the link cannot be found in the network")
            fromnode = allNodes[thelink['from']]
            tonode = allNodes[thelink['to']]
            fromX = float(fromnode['x'])
            fromY = float(fromnode['y'])
            points.append(Point(fromX, fromY))
            toX = float(tonode['x'])
            toY = float(tonode['y'])
            points.append(Point(toX, toY))
        # Create the lineString from the points
        linestring = LineString(points)
        allRoutes[trID] = {'id': trID, 'ls': linestring}
        # allRoutes.append(linestring)

print("doing ESRI conversion")
# now do the conversion to shapefile
esri = Shapely2ESRI(outfilepath, 'write', Shapely2ESRI.SHP_LINE_TYPE, projectionfilepath)
esri.open()
# esri.writeAll(allRoutes)
esri.addField('routeID')
for k in allRoutes:
    esri.writeNext(allRoutes[k]['ls'], {'routeID': allRoutes[k]['id']})
esri.close()

print("parsed schedule file and written shapely file to " + outfilepath)
