#!/usr/bin/python3

from freebox_crystal import deamon

ip='localhost'
api_key='***'

out_sensors = {'Switch': 529, 'WAN': 530}
in_sensors = {'WAN': 528}

domoticz_processor = deamon.DomoticzProcessor('http://'+ip+':8080', api_key, out_sensor_dict=out_sensors,
                                              in_sensor_dict=in_sensors, buffer_size=1)
deamon = deamon.Deamon(processor=domoticz_processor, frequency=10)
deamon.start()
