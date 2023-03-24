# yamale examples

YAMLでパラメータを定義したときに、記入誤りを防止するための防御策としてyamaleを利用する。

https://github.com/23andMe/Yamale


<br><br>

## 注意事項

mapのキーに制約を付けるのは難しい。

これなら動く。

```yaml
parameters:
  device_attr: map(include('device_attr_type'), key=enum('cr1', 'cr2'))
```

key=include('')は機能しない。

```yaml
parameters:
  device_attr: map(include('device_attr_type'), key=include('intf_name_type'))

---

intf_name_type: enum('cr1', 'cr2)
```


## スキーマの例

```yaml

parameters:
  device_attr: map(include('device_attr_type'), key=enum('cr1', 'cr2'))

---

device_attr_type:
  hostname: str()
  bfd_attr: include('bfd_attr_type')
  bgp_attr: include('bgp_attr_type')
  ospf_attr: include('ospf_attr_type')
  interface_attr: |
    subset(
      map(include('interface_attr_type'), key=enum('CR1', 'CR2', 'ER01', 'ER02')),
      map(include('loopback_type'), key=enum('LOOPBACK'))
    )

bfd_attr_type:
  echo_disables: list(enum('CR1', 'CR2', 'ER01', 'ER02'))

bgp_attr_type:
  confederation_peers: list(int())
  router_id: ip(version=4)
  cluster_id: ip(version=4)

ospf_attr_type:
  router_id: ip(version=4)
  default_information_metric: int()
  interface_attr: map(include('ospf_intf_attr_type', required=False))

ospf_intf_attr_type:
  network_type: enum('point-to-point')
  cost: int()
  bfd: include('ospf_intf_bfd_type', required=False)

ospf_intf_bfd_type:
  minimum_interval: int()
  multiplier: int()

loopback_type:
  ifname: str()
  is_upstream: bool()
  ipv4_prefix: ip(version=4)
  ipv4_len: int()
  ipv4_mask: ip(version=4)
  ipv6_prefix: ip(version=6)
  ipv6_len: int()
  ipv4_address: ip(version=4)
  ipv6_address: ip(version=6)

interface_attr_type:
  ifname: str()
  is_upstream: bool()
  ipv4_prefix: ip(version=4)
  ipv4_len: int()
  ipv4_mask: ip(version=4)
  ipv6_prefix: ip(version=6)
  ipv6_len: int()
  ipv4_address: ip(version=4)
  ipv6_address: ip(version=6)
  ipv6_link_local_address: ip(version=6)
  description: str(required=False)
  mtu: int(required=False)
  bundle_id: int(required=False)
  bundle_minimum_active_links: int(required=False)
  bundles: include('bundles_type', required=False)
  peer: include('peer_type', required=False)

peer_type:
  ifname: str(required=False)
  description: str(required=False)
  ipv4_address: ip(version=4)
  ipv6_address: ip(version=6)
  ipv6_link_local_address: ip(version=6, required=False)
  mtu: int(required=False)

bundles_type: list(include('bundles_intf_type'))

bundles_intf_type:
  ifname: str()
  description: str()
```

<br><br>

## データの例

```yaml
parameters:
  device_attr:
    cr1:
      hostname: cr1

      bfd_attr:
        echo_disables:
          - CR2
          - ER01
          - ER02

      bgp_attr:
        confederation_peers:
          - 65001
          - 65002
        router_id: 0.0.0.1
        cluster_id: 0.0.0.1

      ospf_attr:
        router_id: 0.0.0.1
        default_information_metric: 3
        interface_attr:
          LOOPBACK:
          CR2:
            network_type: point-to-point
            cost: 3
            bfd:
              minimum_interval: 500
              multiplier: 5
          ER01:
            network_type: point-to-point
            cost: 3
            bfd:
              minimum_interval: 500
              multiplier: 5
          ER02:
            network_type: point-to-point
            cost: 3

      interface_attr:

        LOOPBACK:
          ifname: Loopback999
          #
          is_upstream: true
          ipv4_prefix: 192.168.255.9
          ipv4_len: 32
          ipv4_mask: 255.255.255.255
          ipv6_prefix: 2001:db8::9
          ipv6_len: 128
          #
          ipv4_address: 192.168.255.9
          ipv6_address: 2001:db8::9

        CR2:
          ifname: Bundle-Ether1
          #
          is_upstream: true
          ipv4_prefix: 10.1.50.208
          ipv4_len: 30
          ipv4_mask: 255.255.255.252
          ipv6_prefix: '2001:db8:e200:170::'
          ipv6_len: 64
          #
          description: CR1-CR2
          ipv4_address: 10.1.50.209
          ipv6_link_local_address: fe80::170:1
          ipv6_address: 2001:db8:e200:170::170:1
          bundle_id: 1
          bundle_minimum_active_links: 1
          bundles:
            -
              ifname: HundredGigE0/0/0/3
              description: cr2(Hu0/0/0/3)
            -
              ifname: HundredGigE0/0/0/11
              description: cr2(Hu0/0/0/11)

        ER01:
          ifname: TenGigE0/0/0/16
          #
          is_upstream: true
          ipv4_prefix: 10.1.50.128
          ipv4_len: 30
          ipv4_mask: 255.255.255.252
          ipv6_prefix: '2001:db8:e200:150::'
          ipv6_len: 64
          #
          description: er01(Te0/0/0/2)
          ipv4_address: 10.1.50.129
          ipv6_link_local_address: fe80::150:1
          ipv6_address: 2001:db8:e200:150::150:1
          mtu: 4484
          peer:
            ifname: TenGigE0/0/2/1
            description: cr1(Te0/0/0/16)
            ipv4_address: 10.1.50.130
            ipv6_link_local_address: fe80::150:2
            ipv6_address: 2001:db8:e200:150::150:2
            mtu: 4484


        ER02:
          ifname: TenGigE0/0/0/17
          #
          is_upstream: true
          ipv4_prefix: 10.1.50.132
          ipv4_len: 30
          ipv4_mask: 255.255.255.252
          ipv6_prefix: '2001:db8:e200:151::'
          ipv6_len: 64
          #
          description: er02(Te0/0/0/2)
          ipv4_address: 10.1.50.133
          ipv6_link_local_address: fe80::151:1
          ipv6_address: 2001:db8:e200:151::151:1
          mtu: 4484
          peer:
            ifname: TenGigE0/0/2/1
            description: cr1(Te0/0/0/17)
            ipv4_address: 10.1.50.134
            ipv6_link_local_address: fe80::151:2
            ipv6_address: 2001:db8:e200:151::151:2
            mtu: 4484
```
