import unittest
from freebox_crystal import parser
import http.server
import socketserver
import threading


class HttpServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        handler = http.server.SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", port), handler)

    def run(self):
        self.httpd.serve_forever()

    def close(self):
        self.httpd.server_close()
        self.httpd.shutdown()


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = parser.InfoParser()
        self.fbx_info = self.parser.parse_file('data/fbx_info.txt')

    def test_general_info(self):
        self.assertEqual(self.fbx_info.firmware_version, '1.5.11')
        self.assertEqual(self.fbx_info.model, 'Freebox ADSL')
        self.assertEqual(self.fbx_info.uptime_in_seconds, (((36 * 24 + 18) * 60) + 49) * 60)

    def test_parse_uptime(self):
        self.assertEqual(parser.parse_uptime('5 jours'), 5 * 24 * 60 * 60)
        self.assertEqual(parser.parse_uptime('3 heures'), 3 * 60 * 60)
        self.assertEqual(parser.parse_uptime('5 jours, 2 heures'), (5 * 24 + 2) * 60 * 60)
        self.assertEqual(parser.parse_uptime('9 jours, 13 heures, 21 minutes'), ((9 * 24 + 13) * 60 + 21) * 60)
        self.assertEqual(parser.parse_uptime('5 jours, 13 secondes'), 5 * 24 * 60 * 60 + 13)

    def test_network_interface(self):
        self.assertEqual(len(self.fbx_info.network_interfaces), 4)

        self.assertEqual(self.fbx_info.network_interfaces['WAN'].status, 'ok')
        self.assertEqual(self.fbx_info.network_interfaces['Ethernet'].status, 'ok')
        self.assertEqual(self.fbx_info.network_interfaces['USB'].status, 'Non connecté')
        self.assertEqual(self.fbx_info.network_interfaces['Switch'].status, '100baseTX-FD')

        self.assertEqual(self.fbx_info.network_interfaces['WAN'].throughput_in, 10)
        self.assertEqual(self.fbx_info.network_interfaces['Ethernet'].throughput_in, 1346)
        self.assertEqual(self.fbx_info.network_interfaces['USB'].throughput_in, 0)
        self.assertEqual(self.fbx_info.network_interfaces['Switch'].throughput_in, 2)

        self.assertEqual(self.fbx_info.network_interfaces['WAN'].throughput_out, 43)
        self.assertEqual(self.fbx_info.network_interfaces['Ethernet'].throughput_out, 87)
        self.assertEqual(self.fbx_info.network_interfaces['USB'].throughput_out, 0)
        self.assertEqual(self.fbx_info.network_interfaces['Switch'].throughput_out, 642)

    def test_dhcp(self):
        self.assertEqual(self.fbx_info.dhcp_map['70:EE:CC:CC:CC:CC'], '192.168.0.10')
        self.assertEqual(self.fbx_info.dhcp_map['F4:F5:CC:CC:CC:CC'], '192.168.0.12')
        self.assertEqual(self.fbx_info.dhcp_map['A8:9C:CC:CC:CC:CC'], '192.168.0.13')

    def test_url_parsing(self):
        port = 18181
        http_server = HttpServer(port)
        http_server.start()
        info = self.parser.parse_url('http://localhost:'+str(port)+'/data/fbx_info.txt', 'utf-8')

        self.assertEqual(info.firmware_version, '1.5.11')
        self.assertEqual(info.model, 'Freebox ADSL')
        self.assertEqual(info.uptime_in_seconds, (((36 * 24 + 18) * 60) + 49) * 60)
        http_server.close()


if __name__ == '__main__':
    unittest.main()
