#!/usr/bin/env python

import logging
import re

# logger settings
logger = logging.getLogger(__name__)

intf_dict = {
    'generic': {
        'Eth': 'Ethernet',
        'Lo': 'Loopback',
        'lo': 'Loopback',
        'Fa': 'FastEthernet',
        'Fas': 'FastEthernet',
        'Po': 'Port-channel',
        'PO': 'Port-channel',
        'Null': 'Null',
        'Gi': 'GigabitEthernet',
        'Gig': 'GigabitEthernet',
        'GE': 'GigabitEthernet',
        'Te': 'TenGigabitEthernet',
        'Ten': 'TenGigabitEthernet',
        'Tw': 'TwoGigabitEthernet',
        'Two': 'TwoGigabitEthernet',
        'Twe': 'TwentyFiveGigE',
        'Fi': 'FiveGigabitEthernet',
        'Fiv': 'FiveGigabitEthernet',
        'Fif': 'FiftyGigE',
        'Fifty': 'FiftyGigabitEthernet',
        'mgmt': 'mgmt',
        'Vl': 'Vlan',
        'Tu': 'Tunnel',
        'Hs': 'HSSI',
        'AT': 'ATM',
        'Et': 'Ethernet',
        'BD': 'BDI',
        'Se': 'Serial',
        'Fo': 'FortyGigabitEthernet',
        'For': 'FortyGigabitEthernet',
        'Hu': 'HundredGigE',
        'Hun': 'HundredGigE',
        'TwoH': 'TwoHundredGigabitEthernet',
        'Fou': 'FourHundredGigE',
        'vl': 'vasileft',
        'vr': 'vasiright',
        'BE': 'Bundle-Ether',
        'tu': 'Tunnel',
        'M-E': 'M-Ethernet',  # comware
        'BAGG': 'Bridge-Aggregation',  # comware
        'Ten-GigabitEthernet': 'TenGigabitEthernet',  # HP
        'Wl': 'Wlan-GigabitEthernet',
        'Di': 'Dialer',
        'Vi': 'Virtual-Access',
        'Ce': 'Cellular',
        'Vp': 'Virtual-PPP',
        'pw': 'pseudowire'
    },
    'iosxr': {
        'BV': 'BVI',
        'BE': 'Bundle-Ether',
        'BP': 'Bundle-POS',
        'Eth': 'Ethernet',
        'Fa': 'FastEthernet',
        'Gi': 'GigabitEthernet',
        'Te': 'TenGigE',
        'Tf': 'TwentyFiveGigE',
        'Fo': 'FortyGigE',
        'Fi': 'FiftyGigE',
        'Hu': 'HundredGigE',
        'Th': 'TwoHundredGigE',
        'Fh': 'FourHundredGigE',
        'Tsec': 'tunnel-ipsec',
        'Ti': 'tunnel-ip',
        'Tm': 'tunnel-mte',
        'Tt': 'tunnel-te',
        'Tp': 'tunnel-tp',
        'IMA': 'IMA',
        'IL': 'InterflexLeft',
        'IR': 'InterflexRight',
        'Lo': 'Loopback',
        'Mg': 'MgmtEth',
        'Ml': 'Multilink',
        'Nu': 'Null',
        'POS': 'POS',
        'Pw': 'PW-Ether',
        'Pi': 'PW-IW',
        'SRP': 'SRP',
        'Se': 'Serial',
        'CS': 'CSI',
        'G0': 'GCC0',
        'G1': 'GCC1',
        'nG': 'nVFabric-GigE',
        'nT': 'nVFabric-TenGigE',
        'nF': 'nVFabric-FortyGigE',
        'nH': 'nVFabric-HundredGigE'
    }
}

cisco_intf_name_list = list(set([ intf_name for intf_maps in intf_dict.values() for intf_name in intf_maps.values() ]))


def split_intf_name_and_number(intf: str):
    name = None
    m = re.search(r'(?P<name>[-a-zA-Z]+)', intf)
    if m:
        name = m.group('name')

    number = None
    m = re.search(r'(?P<number>\d[\w./]*)', intf)
    if m:
        number = m.group('number')

    return (name, number)


def convert_intf_name(intf:str, os='generic'):

    intf_name, intf_number = split_intf_name_and_number(intf)
    if intf_name is not None and intf_number is not None:
        try:
            os_type_dict = intf_dict[os]
        except KeyError:
            logger.error(f'unknown os: {os}')
        else:
            if intf_name in os_type_dict.keys():
                return os_type_dict[intf_name] + intf_number
            else:
                return intf[0].capitalize() + intf[1:].replace(' ', '').replace('ethernet', 'Ethernet')
    else:
        return intf


if __name__ == '__main__':
    import sys

    def main():

        # print(cisco_intf_name_list)

        test_intfs = [
            'Gig0/0',
            'Te1/0/1',
            'Twe1/0/1',
            'Hu1/0/49',
        ]

        for intf in test_intfs:
            normalized_intf_name = convert_intf_name(intf=intf)
            print(f'{intf} is normazlied as {normalized_intf_name}')

        return 0

    sys.exit(main())
