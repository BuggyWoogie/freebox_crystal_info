import re
import sys
import urllib.request


def parse_uptime(uptime):
    space_pattern = re.compile('\\s+')

    def extract_number(x):
        return int(space_pattern.split(x[0])[0])

    result = 0
    days = re.compile('[0-9]+\\s+jour').findall(uptime)
    if days:
        result += extract_number(days) * 24 * 60 * 60
    hours = re.compile('[0-9]+\\s+heure').findall(uptime)
    if hours:
        result += extract_number(hours) * 60 * 60
    minutes = re.compile('[0-9]+\\s+minut').findall(uptime)
    if minutes:
        result += extract_number(minutes) * 60
    seconds = re.compile('[0-9]+\\s+second').findall(uptime)
    if seconds:
        result += extract_number(seconds)
    return result


class InfoParser(object):
    def __init__(self):
        pass

    def parse_url(self, url='http://192.168.0.254/pub/fbx_info.txt', encoding='latin'):
        txt_info = urllib.request.urlopen(url).read()
        return self.parse_string(txt_info.decode(encoding))

    def parse_file(self, path):
        file = open(path, 'r')
        txt_info = file.read()

        file.close()
        return self.parse_string(txt_info)

    def parse_string(self, txt_info):
        raw_info_parts = re.compile('\\s*=+\\s*').split(txt_info)
        new_line_pattern = re.compile('\\s*\\n\\s*')
        info_lines = [new_line_pattern.split(part) for part in raw_info_parts if part != '']

        # titles are the last lines of the "parts"
        colon_pattern = re.compile('\\s*:\\s*')
        titles = [colon_pattern.split(lines[-1])[0] for lines in info_lines[:-1]]
        info_parts = [lines[:-1] for lines in info_lines[1:]]

        info_dict = dict(zip(titles, info_parts))
        fbx_info = FreeboxInfo()
        self.parse_general_information(info_dict['Informations générales'], fbx_info)
        self.parse_network(info_dict['Réseau'], fbx_info)
        return fbx_info

    def parse_general_information(self, lines, fbx_info):
        space_pattern = re.compile('\\s\\s+')
        for line in lines:
            parts = space_pattern.split(line)
            title = parts[0]
            content = parts[1]
            if re.compile('mod(e|è)l').findall(title.lower()):
                fbx_info.model = content
            elif 'firmware' in title.lower():
                fbx_info.firmware_version = content
            elif 'mode' in title.lower() and 'connection' in title.lower():
                fbx_info.connexion_mode = content
            elif re.compile('temps.*route').findall(title.lower()):
                fbx_info.uptime_in_seconds = parse_uptime(content)
            else:
                sys.stderr.write(f'unrecognized information: {title}\n')

    def parse_network_title(self, title):
        clean_title = re.compile('\\s*:\\s*').split(title)[0].lower()
        if 'dhcp' in clean_title and 'attribution' in clean_title:
            return 'dhcp'
        elif 'redirection' in clean_title and 'port' in clean_title:
            return 'port_redirections'
        elif 'interface' in clean_title and 'réseau' in clean_title:
            return 'network_interfaces'
        else:
            return clean_title

    def parse_network(self, lines, fbx_info):
        parts = re.compile('\\s*\\n+\\s*-+\\s*\\n+\\s*').split('\n'.join(lines))
        lines_of_parts = [part.split('\n') for part in parts]
        titles = ['main'] + [self.parse_network_title(lp[-1]) for lp in lines_of_parts[:-1]]
        network_info = dict(zip(titles, [lp[:-1] for lp in lines_of_parts[:-1]] + [lines_of_parts[-1]]))
        fbx_info.network_interfaces = self.parse_network_interfaces(network_info['network_interfaces'])
        fbx_info.dhcp_map = self.parse_dhcp_map(network_info['dhcp'])

    def parse_dhcp_map(self, lines):
        return dict([
            self.parse_dhcp(line) for line in lines if ('adresse' not in line.lower()) and ('--' not in line)
        ])

    def parse_dhcp(self, line):
        [mac, ip] = re.compile(r'\s+').split(line)
        return mac, ip

    def parse_network_interface(self, line):
        parts = re.compile(r'\s\s+').split(line)
        title = parts[0]
        index = 2
        if re.compile(r'^[0-9]+ ko/s').match(parts[1]):
            index = 1
            status = 'ok'
        elif parts[1] == 'Ok' or parts[1] == 'OK':
            status = 'ok'
        else:
            status = parts[1]
        if len(parts) > index:
            throughput_in = int(parts[index].split(' ')[0])
            throughput_out = int(parts[index+1].split(' ')[0])
            return title, NetworkInterface(title, status, throughput_in, throughput_out)
        else:
            return title, NetworkInterface(title, status)

    def parse_network_interfaces(self, lines):
        return dict([
            self.parse_network_interface(l) for l in lines if ('--' not in l) and ('débit' not in l.lower())
        ])


class FreeboxInfo(object):
    def __str__(self):
        return """{{
    model: {0}
    firmware: {1}
    connection_mode: {2}
    uptime: {3} seconds
    network: {4}
    dhcp: {5}
}}""".format(self.model, self.firmware_version, self.connexion_mode, self.uptime_in_seconds,
             "".join(['\n        {}: {}'.format(k, self.network_interfaces[k]) for k in self.network_interfaces]),
             "".join(['\n        {}: {}'.format(k, self.dhcp_map[k]) for k in self.dhcp_map]))


class NetworkInterface(object):
    def __init__(self, name, status='ok', throughput_in=0, throughput_out=0):
        self.name = name
        self.status = status
        self.throughput_in = throughput_in
        self.throughput_out = throughput_out

    def __str__(self):
        return 'NetworkInterface(name={}, status={}, in={}, out={})'\
            .format(self.name, self.status, self.throughput_in, self.throughput_out)
