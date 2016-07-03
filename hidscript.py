from attack import NordicGenericHID as hid

scriptentryblank = {
    "meta": False,
    "shift": False,
    "alt": False,
    "ctrl": False,
    "hid": 0,
    "char": '',
    "sleep": 0
}
    
def __init__(self):
        pass

def chartohid(char):
    for k, v in hid.hid_map.iteritems():
        if v[0] == char:
            return k, False
        elif v[1] == char:
            return k, True

def scripttohid(script):
        entries = []
        scriptlines = script.split("\n")
        print scriptlines
        for line in scriptlines:

            if line.startswith('ALT'):
                entry = scriptentryblank.copy()
                entry['alt'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = chartohid(entry['char'])
                entries.append(entry)

            elif line.startswith("GUI") or line.startswith('WINDOWS') or line.startswith('COMMAND'):
                entry = scriptentryblank.copy()
                entry['meta'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = chartohid(entry['char'])
                entries.append(entry)

            elif line.startswith('CTRL') or line.startswith('CONTROL'):
                entry = scriptentryblank.copy()
                entry['ctrl'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = chartohid(entry['char'])
                entries.append(entry)

            elif line.startswith('SHIFT'):
                entry = scriptentryblank.copy()
                entry['shift'] = True
                entry['char'] = line.split()[1]
                entry['hid'], entry['shift'] = chartohid(entry['char'])
                entries.append(entry)

            elif line.startswith("ESC") or line.startswith('APP') or line.startswith('ESCAPE'):
                entry = scriptentryblank.copy()
                entry['char'] = "[ESC]"
                entry['hid'], entry['shift'] = chartohid(entry['char'])
                entries.append(entry)

            elif line.startswith("DELAY"):
                entry = scriptentryblank.copy()
                entry['sleep'] = line.split()[1]
                entries.append(entry)

            elif line.startswith("STRING"):
                for char in " ".join(line.split()[1:]):
                    entry = scriptentryblank.copy()
                    entry['char'] = char
                    entry['hid'], entry['shift'] = chartohid(char)
                    entries.append(entry)

            elif line.startswith("ENTER"):
                entry = scriptentryblank.copy()
                entry['char'] = "\n"
                entry['hid'], entry['shift'] = chartohid('\n')
                entries.append(entry)
            else:
                print "CAN'T PROCESS... %s" % line