class Waypoint():
    def __init__(self, waypoint):
        def latlon_convert(latlon):
            if latlon.endswith('N'):
                degrees = float(latlon[0:2])
                minutes = float(latlon[2:4])
                seconds = float(latlon[4:6])
                return round((degrees + (minutes/60) + (seconds/3600)), 5)
            if latlon.endswith('W'):
                degrees = float(latlon[0:3])
                minutes = float(latlon[3:5])
                seconds = float(latlon[5:7])
                return round(-1 * (degrees + (minutes/60) + (seconds/3600)), 5)
        fix = []
        lat = []
        lon = []
        artcc = []
        fix_type = []
        with open('NATFIX.txt') as fix_file:
            for rows in fix_file:
                if rows.startswith('I') == True:
                    fix.append(rows[2:7].strip(' '))
                    lat.append(latlon_convert(rows[8:15]))
                    lon.append(latlon_convert(rows[16:24]))
                    artcc.append(rows[26:29])
                    fix_type.append(rows[37:].strip('\n'))
                    
        self.fixes = waypoint.upper()
        index = fix.index(self.fixes)        
        self.type = fix_type[index]
        self.coords = lon[index], lat[index]
        self.artcc = artcc[index]
        
    def fix_details(self):
        return self.type, self.coords, self.artcc
    
class Center_Boundary():
    def __init__(self, center):
        self.lats = []
        self.lons = []
        with open('Center_boundaries.csv') as csv:
            for row in csv:
                if row.startswith(center):
                    row = row.split(',')
                    raw_lat, raw_lon = row[1], row[2]
                    lat = float(raw_lat[0:2] + '.' + raw_lat[2:].strip('N'))
                    lon = '-' + raw_lon[0:3].lstrip('0') + '.' + raw_lon[3:].strip('\n').strip('W')
                    lon = float(lon)
                    self.lats.append(lat)
                    self.lons.append(lon)
        latlon_list = list(zip(self.lons, self.lats))
        first_coord = (self.lons[0], self.lats[0])
        latlon_list.append(first_coord)
        self.latlons = [lon[0] for lon in latlon_list], [lat[1] for lat in latlon_list]
            
class Routes():
    def __init__(self, route):
        def latlon_convert(latlon):
            if latlon.endswith('N'):
                degrees = float(latlon[0:2])
                minutes = float(latlon[3:5])
                seconds = float(latlon[7:10])
                return round((degrees + (minutes/60) + (seconds/3600)), 5)
            if latlon.endswith('W'):
                degrees = float(latlon[0:3])
                minutes = float(latlon[3:5])
                seconds = float(latlon[7:-2])
                return round(-1 * (degrees + (minutes/60) + (seconds/3600)), 5)
        fix_names = []
        fix_coords = []
        with open('AWY.txt') as route_file:
            for rows in route_file:
                if rows.startswith('AWY2'):
                    name = rows[4:9].strip(' ')
                    if name == route.upper():
                        star_index = rows.index('*')
                        fix_name = rows[116:120].strip(" ")
                        if fix_name == '':
                            fix_name = rows[15:25].strip(" ")
                        fix_names.append(fix_name)
                        latitude = latlon_convert(rows[83:97].strip(" "))
                        longitude = latlon_convert(rows[97:111].strip(" "))
                        fix_coords.append((longitude, latitude))

        self.fixes = fix_names
        self.coords = fix_coords
        self.zipped = list(zip(self.fixes, self.coords))
        
class STAR():
    def __init__(self, route):
        def latlon_convert(latlon):
            if latlon.startswith('N'):
                degrees = float(latlon[1:3])
                minutes = float(latlon[4:6])
                seconds = float(latlon[6:10])
                return round((degrees + (minutes/60) + (seconds/3600)), 5)
            if latlon.startswith('W'):
                degrees = float(latlon[1:4])
                minutes = float(latlon[4:6])
                seconds = float(latlon[6:-1])
                return round(-1 * (degrees + (minutes/60) + (seconds/3600)), 5)
        route_package = []
        with open('STARDP.txt') as route_file:
            ID_grabber = ''
            for rows in route_file:
                name = rows[38:51].strip(' ')
                row_ID = rows[0:5]
                if route in name:
                    ID_grabber = rows[0:5]
                    route_package.append(rows.strip('\n'))
                elif row_ID == ID_grabber:
                    route_package.append(rows.strip('\n'))
        whole_routeidx = []
        for index, rows in enumerate(route_package):
            if route in rows:
                whole_routeidx.append(index)
        stratified = [] 
        iterable = iter(whole_routeidx)
        next(iterable)
        for ind in whole_routeidx:
            try:
                end = next(iterable)
                stratified.append(route_package[ind:end])
            except:
                end = len(route_package)
                stratified.append(route_package[ind:end])
        transitions = {}
        trunks = {}
        airports = []
        toggle1 = False
        toggle2 = False
        for sections in stratified:
            transition_name = ''
            fix_list = []
            for rows in sections:
                if "TRANSITION" in rows:
                    toggle1 = True
                    transition_name = rows[30:36].strip()
                elif route in rows and "TRANSITION" not in rows:
                    toggle2 = True
                    transition_name = rows[30:36].strip()
            if toggle1 == True:
                for rows in sections:
                    fix_name = rows[30:36].strip()
                    lat = latlon_convert(rows[13:21])
                    lon = latlon_convert(rows[21:30])
                    fix_list.append((fix_name, lon, lat))
            elif toggle2 == True:
                for rows in sections:
                    if 'AA' not in rows:
                        fix_name = rows[30:36].strip()
                        lat = latlon_convert(rows[13:21])
                        lon = latlon_convert(rows[21:30])
                        fix_list.append((fix_name, lon, lat))

                    elif 'AA' in rows[10:12]:
                        airports.append(rows[30:36].strip())

            if len(fix_list) > 0 and toggle1 == True:
                transitions[transition_name]=fix_list
            elif len(fix_list) > 0 and toggle2 == True:
                trunks[fix_list[-1][0]]=fix_list
        
        
        splits = {'trunks':trunks,'transitions':transitions}
        
        
                            
        self.fixes = splits
        self.coords = self.get_coords(self.fixes)
        self.transitions = transitions
        self.trunks = trunks
        self.airports = airports
        self.transition_set = False
        self.trunk_set = False
        
    def get_coords(self, split_dict):
            coord_list = []
            if type(split_dict) == dict:
                for key, value in split_dict.items():
                    for key, value in value.items():
                        for fixes in value:
                            coord_list.append((fixes[1], fixes[2]))
            elif type(split_dict) == tuple:
                dictionary = split_dict[0]
                for fixes in split_dict[1]:
                    coord_list.append((fixes[1],fixes[2]))
                coord_list.append(list(dictionary.items()))
            return coord_list
        
    def set_trunk(self,trunk):
        trunk = trunk.upper()
        routing = self.fixes['trunks'][trunk]
        self.fixes = (routing,self.transitions)
        self.trunk_set = True
        
    def set_transition(self,transition):
        transition = transition.upper()
        #print(self.fixes)
        if self.trunk_set == True:
            routing = self.fixes[1][transition]
            self.fixes = self.fixes[0][:-1] + [fix for fix in routing]
            self.coords = self.get_coords(self.fixes)
        elif self.trunk_set != True:
            routing = self.fixes['transitions'][transition]
            self.fixes = (self.trunks,routing)
            self.coords = self.get_coords(self.fixes)
        self.transition_set = True
class SID():
    def __init__(self, route):
        route_type = ''
        def latlon_convert(latlon):
            if latlon.startswith('N'):
                degrees = float(latlon[1:3])
                minutes = float(latlon[4:6])
                seconds = float(latlon[6:10])
                return round((degrees + (minutes/60) + (seconds/3600)), 5)
            if latlon.startswith('W'):
                degrees = float(latlon[1:4])
                minutes = float(latlon[4:6])
                seconds = float(latlon[6:-1])
                return round(-1 * (degrees + (minutes/60) + (seconds/3600)), 5)
        route_package = []        
    
        with open('STARDP.txt') as route_file:
            ID_grabber = ''
            for rows in route_file:
                name = rows[38:51].strip(' ')
                row_ID = rows[0:5]
                if route in name:
                    ID_grabber = rows[0:5]
                    route_package.append(rows.strip('\n'))
                elif row_ID == ID_grabber:
                    route_package.append(rows.strip('\n'))
        whole_routeidx = []
        for index, rows in enumerate(route_package):
            if route in rows:
                whole_routeidx.append(index)
                
        stratified = [] 
        iterable = iter(whole_routeidx)
        next(iterable)
        for ind in whole_routeidx:
            try:
                end = next(iterable)
                stratified.append(route_package[ind:end])
            except:
                end = len(route_package)
                stratified.append(route_package[ind:end])
        transition = {}
        trunks = {}
        airports = []
        route_string = []
        toggle1 = False
        toggle2 = False
        for sections in stratified:
            transition_name = ''
            fix_list = []
            for rows in sections:
                if "TRANSITION" in rows:
                    toggle1 = True
                    transition_name = rows[30:36].strip()
                elif "TRANSITION" not in rows and route in rows:
                    toggle2 = True
                    transition_name = rows[30:36].strip()
            if toggle1 == True:
                for rows in sections:
                    fix_name = rows[30:36].strip()
                    lat = latlon_convert(rows[13:21])
                    lon = latlon_convert(rows[21:30])
                    fix_list.append((fix_name, lon, lat))
                    
            elif toggle2 == True:
                for rows in sections:
                    fix_name = rows[30:36].strip()
                    lat = latlon_convert(rows[13:21])
                    lon = latlon_convert(rows[21:30])
                    fix_list.append((fix_name, lon, lat))
                    if 'AA' not in rows[10:12]:
                        fix_name = rows[30:36].strip()
                        lat = latlon_convert(rows[13:21])
                        lon = latlon_convert(rows[21:30])
                        route_string.append((fix_name, lon, lat))

                    elif 'AA' in rows[10:12]:
                        airports.append(rows[30:36].strip())
            if len(fix_list) > 0 and toggle1 == True:
                transition[fix_list[-1][0]]=fix_list
            elif len(fix_list) > 0 and toggle2 == True:
                trunks[transition_name]=route_string
        splits = {'trunks':trunks,'transitions':transition}
        self.transitions = transition
        self.trunks = trunks
        self.fixes = splits
        self.coords = [(fix[1], fix[2]) for fix in route_string]
        self.route_string = route_string
        self.airports = airports
        self.type = route_type
        self.transition_set = False
        self.trunk_set = False
        
    def set_trunk(self,trunk):
        trunk = trunk.upper()
        routing = self.fixes['trunks'][trunk]
        self.fixes = (routing,self.transitions)
        self.trunk_set = True
        
    def set_transition(self,transition):
        transition = transition.upper()
        #print(self.fixes)
        if self.trunk_set == True:
            routing = self.fixes[1][transition]
            self.fixes = self.fixes[0][:-1] + [fix for fix in routing]
        elif self.trunk_set != True:
            try:
                routing = self.fixes['transitions'][transition]
                self.fixes = (self.trunks,routing)
            except:
                pass
        self.transition_set = True
class route_decode():
    def __init__(self, route):
        departure = [route[0]]
        enroute = []
        arrival = []
        def find_numbers(fix):
            toggle1 = False
            for chars in fix:
                try:
                    chars = int(chars)
                    toggle1 = True
                except ValueError:
                    pass
            if toggle1 == True:
                return fix
                
        for items in route[:3]:
            appendable = find_numbers(items)
            if appendable != None:
                departure.append(appendable)
                departure.append(route[2])
        for items in route[-3:]:
            appendable = find_numbers(items)
            if appendable != None:
                arrival.append(route[-3])
                arrival.append(appendable)
            if 'K' in items and len(items) == 4:
                arrival.append(items)
        for index, items in enumerate(route):
                if items not in departure and items not in arrival:
                    try:
                        enroute.append(Waypoint(items).fixes)
                    except:
                        appendable = Routes(items).fixes
                        start = 0
                        end = -1
                        try:
                            next_fix = route[index+1]
                        except:
                            pass
                        for fixes in appendable:
                            if fixes == enroute[-1]:
                                start = appendable.index(fixes) + 1
                            elif fixes == arrival[0]:
                                end = appendable.index(fixes)
                            elif fixes == next_fix:
                                end = appendable.index(fixes)
                        appendable = appendable[start:end]
                        
                        for fixes in appendable:
                            enroute.append(fixes)
            
        self.SID = departure[0]
        self.SID_transition = departure[1]
        self.STAR_transition = arrival[0]
        self.STAR = arrival[1]
        self.whole_route = departure + enroute + arrival
        self.departure_set = False
        self.arrival_set = False

    def set_departure(self):
        airport = self.whole_route[0]
        sid = self.whole_route[1]
        trans = self.whole_route[2]
        sid_transition = SID(sid)
        try:
            sid_transition.set_transition(trans)
            sid_trans_fixes = [tuple[0] for tuple in sid_transition.fixes[1]]
            self.whole_route = [airport, (sid + '*')] + sid_trans_fixes + self.whole_route[3:]
        except:
            self.whole_route = [airport, (sid + '*'), trans] + self.whole_route[3:]
        self.departure_set = True


    def set_arrival(self):
        airport = self.whole_route[-1]
        star = self.whole_route[-2]
        trans = self.whole_route[-3]
        star_transition = STAR(star)
        star_transition.set_transition(trans)
        star_trans_fixes = [tuple[0] for tuple in star_transition.fixes[1]]
        self.whole_route = self.whole_route[:-4]
        for fixes in star_trans_fixes:
            self.whole_route.append(fixes)
        self.whole_route.append(star + '*')
        self.whole_route.append(airport)
        self.arrival_set = True
