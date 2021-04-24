import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.animation import FuncAnimation, PillowWriter
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
from datetime import datetime
from datetime import timedelta
import pygrib
now_dt = datetime.utcnow()
db_filenames = [f for f in listdir('BINs') if isfile(join('BINs', f))]
file_window = 6
sorted_times = sorted(db_filenames, reverse=True)[:file_window]
def get_dt(grb):
    raw_date, raw_time = str(grb.validityDate), str(grb.validityTime)
    year = int(raw_date[0:4])
    if raw_date[4] == '0':
        month = int(raw_date[5])
    else:
        month = int(raw_date[4:6])
    if raw_date[6] == '0':
        day = int(raw_date[-1])
    else:
        day = int(raw_date[-2:])
    if len(raw_time) < 4:
        hour = int(raw_time[0])
        if raw_time[-2:][0] == '0':
            minute = int(raw_time[-1])
        else:
            minute = int(raw_time[-2:])
    else:
        hour = int(raw_time[:2])
        minute = int(raw_time[-2:])

    return datetime(year, month, day, hour, minute)

x1 = -125
x2 = -70
y1 = 25
y2 = 55

viewing_delta = timedelta(hours = 6)
df_list = {}
altitude = 25000
for file_name in sorted_times:
    meters = int(round((altitude / 3.28084), -1))
    grbs = pygrib.open('BINs/' + file_name).select(shortName='cat', level=meters)
    grb_dict = {}
    for grb in grbs:
        grb_dt = get_dt(grb)
        current_dt = now_dt - timedelta(hours=1)
        if grb_dt > now_dt and grb_dt < (now_dt + viewing_delta) or now_dt > grb_dt > current_dt:
            data = grb.data()
            df_list[grb_dt]= {
            'lats':data[1],
            'lons':data[2],
            'values':data[0]
            }
delta_list = []
for key, values in df_list.items():
    delta_list.append(key)
sorted_deltas  = sorted(delta_list)
fig = plt.figure(figsize=[14,8], edgecolor='slategrey', frameon=False)
ax = plt.axes([0., 0., 1., 1.], projection = ccrs.PlateCarree())
def animate(delta, df_list):
    ax.clear()
    level=altitude
    data = df_list[delta]
    lons, lats, values = data['lons'], data['lats'], data['values']
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES)
    ax.set_xlim(left=x1, right=x2)
    ax.set_ylim(bottom=y1, top=y2)
    ax.imshow(values, extent=[x1, x2, y1, y2],  vmax=0.5, origin='lower', cmap='coolwarm')
    title = str(delta) + ' UTC AT ' + str(level) + ' feet'
    ax.set_title(title, fontdict={'fontsize': 20, 'color': 'white'}, y=0.2)

fig.patch.set_alpha(0.)
anim = FuncAnimation(fig, animate, frames =sorted_deltas,fargs=(df_list,), interval=500)
writergif = PillowWriter(fps=1)
anim.save('turbs.gif',writer=writergif, savefig_kwargs={'pad_inches': 0.})

plt.close()
