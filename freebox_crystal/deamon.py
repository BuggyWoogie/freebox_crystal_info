from freebox_crystal import InfoParser
import time
import requests


class Deamon(object):
    def __init__(self,  url='http://192.168.0.254/pub/fbx_info.txt', processor=None, frequency=120, encoding='latin'):
        self.url = url
        self.frequency = frequency
        self.parser = InfoParser()
        self.encoding = encoding
        if processor is None:
            self.processor = InfoPrinter()
        else:
            self.processor = processor

    def start(self):
        while True:
            info = self.parser.parse_url(self.url, self.encoding)
            self.processor.process(info)
            time.sleep(self.frequency)


class InfoPrinter(object):
    def process(self, info):
        print(info)


class DomoticzProcessor(object):
    def __init__(self,  url, api_key, out_sensor_dict=dict(), in_sensor_dict=dict(), buffer_size=6):
        self.url = url
        self.buffer_size = max(buffer_size, 1)
        self.counter = 0
        self.api_key = api_key
        self.out_sensor_dict = out_sensor_dict
        self.in_sensor_dict = in_sensor_dict
        self.in_data_dict = dict([(k, 0) for k in in_sensor_dict.keys()])
        self.out_data_dict = dict([(k, 0) for k in out_sensor_dict.keys()])

    def process(self, info):
        self.counter += 1
        for k in self.in_sensor_dict.keys():
            self.in_data_dict[k] += info.network_interfaces[k].throughput_in
        for k in self.out_sensor_dict.keys():
            print(info.network_interfaces[k])
            self.out_data_dict[k] += info.network_interfaces[k].throughput_out
        if self.counter == self.buffer_size:
            self.counter = 0
            for k in self.in_sensor_dict.keys():
                data = self.in_data_dict[k]
                self.send_to_domoticz(k, data, self.in_sensor_dict)
                self.in_data_dict[k] = 0
            for k in self.out_sensor_dict.keys():
                data = self.out_data_dict[k]
                self.send_to_domoticz(k, data, self.out_sensor_dict)
                self.out_data_dict[k] = 0

    def send_to_domoticz(self, key, data, sensor_dict):
        sensor_id = sensor_dict[key]
        avg_data = str(round(float(data) / self.buffer_size))
        print('Sensor {} is set to {}kB/s'.format(sensor_id, avg_data))
        params = {'type': 'command', 'param': 'udevice', 'idx': sensor_id, 'nvalue': '0', 'svalue': avg_data}
        header = {'Authorization' : 'Basic ' + self.api_key}
        requests.get(self.url+'/json.htm', params=params, headers=header)

