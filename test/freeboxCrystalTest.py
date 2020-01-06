import unittest
from freeboxCrystal import freeboxCrytal


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = freeboxCrytal.InfoParser()
        self.fbx_info = self.parser.parse_file('data/fbx_info.txt')

    def test_general_info(self):
        self.assertEqual(self.fbx_info.firmware_version, '1.5.11')
        self.assertEqual(self.fbx_info.model, 'Freebox ADSL')
        self.assertEqual(self.fbx_info.uptime_in_seconds, (((36 * 24 + 18) * 60) + 49) * 60)

    def test_parse_uptime(self):
        self.assertEqual(freeboxCrytal.parse_uptime('5 jours'), 5*24*60*60)
        self.assertEqual(freeboxCrytal.parse_uptime('3 heures'), 3*60*60)
        self.assertEqual(freeboxCrytal.parse_uptime('5 jours, 2 heures'), (5*24 + 2)*60*60)
        self.assertEqual(freeboxCrytal.parse_uptime('9 jours, 13 heures, 21 minutes'), ((9*24+13)*60 + 21)*60)
        self.assertEqual(freeboxCrytal.parse_uptime('5 jours, 13 secondes'), 5*24*60*60 + 13)

if __name__ == '__main__':
    unittest.main()
