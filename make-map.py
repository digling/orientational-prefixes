from lingpy import *
import mpl_toolkits.basemap as bmp
import matplotlib.pyplot as plt
import unidecode

# get locations 

locs = csv2list('locs.tsv')
locations = {}
for line in locs[1:]:
    locations[unidecode.unidecode(line[0])] = [
            float(line[1]),
            float(line[2])
            ]

m = bmp.Basemap(
        llcrnrlon=100.75,
        llcrnrlat=31.25,
        urcrnrlon=103.25,
        urcrnrlat=32.5,
        resolution='h',
        projection='merc'
        )
m.drawmapboundary(fill_color="blue")
m.drawcoastlines(color="black", linewidth=0.25)
m.drawcountries(color="black", linewidth=0.1)
m.fillcontinents(color="antiquewhite", alpha=0.5, lake_color="blue")
#m.etopo(scale=4)
m.shadedrelief(scale=5)
m.drawrivers(color='blue')


# draw roads
mstlocs = csv2list('mst-locs.tsv')
for source, target in mstlocs[1:]:
    lat1, lon1 = locations[unidecode.unidecode(source)]
    lat2, lon2 = locations[unidecode.unidecode(target)]
    x1, y1 = m(lon1, lat1)
    x2, y2 = m(lon2, lat2)
    plt.plot([x1, x2], [y1, y2], '-', color="green", markersize=2)

for loc, (lat, lon) in locations.items():
    x, y = m(lon, lat)
    plt.plot(x, y, 'o', color='red', markersize=5, markeredgewidth=0.1,
            markeredgecolor='black')
    _x, _y = m(lon+0.01, lat+0.01)
    plt.text(_x, _y, loc, fontsize=3, bbox={"fc": "white", "lw": 0.1,
        "boxstyle": "round,pad=0.1"})


plt.savefig('language_map.pdf')
