import re
import sys


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

    def parse_file(self, path):
        file = open(path, 'r')
        txt_info = file.read()
        file.close()

        # part titles are underlined by '===='. Let's use them as delimiters.
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


class FreeboxInfo(object):
    pass
