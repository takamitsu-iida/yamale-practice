#!/usr/bin/env python

import logging
import os
import sys

import yamale

from schema import Schema, And, Or, Use, Optional, SchemaError
from ipaddress import ip_interface, ip_address, ip_network

from cisco_intf_name import cisco_intf_name_list, split_intf_name_and_number


def here(path=''):
    """相対パスを絶対パスに変換して返却します"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# アプリケーションのホームディレクトリはこのファイルからみて一つ上
app_home = here('..')

# 自身の名前から拡張子を除いてプログラム名を得る
app_name = os.path.splitext(os.path.basename(__file__))[0]

# ディレクトリ
conf_dir = os.path.join(app_home, 'conf')
data_dir = os.path.join(app_home, 'data')


# libフォルダにおいたpythonスクリプトをインポートできるようにするための処理
# このファイルの位置から一つ
lib_dir = os.path.join(app_home, 'lib')
if not lib_dir in sys.path:
    sys.path.append(lib_dir)

#
# ログ設定
#

# ログファイルを置くディレクトリ
log_dir = os.path.join(app_home, 'log')
os.makedirs(log_dir, exist_ok=True)

# ログファイルの名前
log_file = app_name + '.log'
log_path = os.path.join(log_dir, log_file)
# os.remove(log_path)

# ロギングの設定
# レベルはこの順で下にいくほど詳細になる
#   logging.CRITICAL
#   logging.ERROR
#   logging.WARNING --- 初期値はこのレベル
#   logging.INFO
#   logging.DEBUG
#
# ログの出力方法
# logger.debug('debugレベルのログメッセージ')
# logger.info('infoレベルのログメッセージ')
# logger.warning('warningレベルのログメッセージ')

# ロガーを取得
logger = logging.getLogger(__name__)

# ログレベル設定
logger.setLevel(logging.INFO)

# フォーマット
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 標準出力へのハンドラ
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.INFO)
logger.addHandler(stdout_handler)

# ログファイルのハンドラ
file_handler = logging.FileHandler(log_path, 'a+')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)


if __name__ == '__main__':

    def main():

        schema_path = os.path.join(data_dir, 'schema.yaml')
        schema = yamale.make_schema(schema_path)

        data_path = os.path.join(data_dir, 'data.yaml')
        data = yamale.make_data(data_path)

        try:
            yamale.validate(schema, data)
        except yamale.YamaleError as e:
            logger.error('Validation failed!')
            for result in e.results:
                logger.error(f'Error validating data {result.data} with {result.schema}')
                for error in result.errors:
                    logger.error(f'\t{error}')
            return 1
        logger.info('YAML Validation success! 👍')

        #
        # 内容を精査する
        #

        # yamaleのmake_dataは不思議な構造をしていて、これでdictを取り出せる
        parameters = data[0][0].get('parameters')

        try:
            for device_name, device_data in parameters.get('device_attr').items():

                # interface_attrで用いているインタフェース名のリスト
                intf_name_list = list(device_data.get('interface_attr').keys())

                # bfd_attrで使っているインタフェース名がインタフェース名のリストにある？
                echo_disables = device_data['bfd_attr']['echo_disables']
                Schema(intf_name_list).validate(echo_disables)

                # ループバックのアドレス
                loopback_ipv4 = device_data['loopback']['ipv4_address']

                # bgp_attrのrouter_idはループバックアドレス？
                Schema({'router_id': lambda id: id == loopback_ipv4}, ignore_extra_keys=True).validate(device_data['bgp_attr'])

                # ospf_attrで使っているインタフェース名がインタフェース名のリストにある？
                ospf_intfs = list(device_data['ospf_attr']['interface_attr'].keys())
                Schema(intf_name_list).validate(ospf_intfs)

                # ospf_attrのrouter_idはループバックアドレス？
                Schema({'router_id': lambda id: id == loopback_ipv4}, ignore_extra_keys=True).validate(device_data['ospf_attr'])

                for intf_name, intf_data in device_data['interface_attr'].items():

                    # ifnameはシスコのインタフェース名？
                    intf_prefix, intf_num = split_intf_name_and_number(intf_data['ifname'])
                    Schema(cisco_intf_name_list).validate([intf_prefix])

                    # IPv4のプレフィクス情報を取り出してip_networkオブジェクトを作成する
                    ipv4_prefix = intf_data.get('ipv4_prefix')
                    ipv4_mask = intf_data.get('ipv4_mask')
                    ipv4_network = ip_network(f'{ipv4_prefix}/{ipv4_mask}')

                    # ipv4_address情報を取り出してip_interfaceオブジェクトを作成する
                    ipv4_address = intf_data.get('ipv4_address')
                    ipv4_interface = ip_interface(f'{ipv4_address}/{ipv4_mask}')

                    # このインタフェースアドレスがプレフィクスの範囲内に入っているか？
                    try:
                        assert ipv4_interface.network == ipv4_network
                    except AssertionError:
                        logger.error(f'{ipv4_interface} is not in {ipv4_network}')

                    # IPv6のプレフィクス情報を取り出してip_networkオブジェクトを作成する
                    ipv6_prefix = intf_data.get('ipv6_prefix')
                    ipv6_len = intf_data.get('ipv6_len')
                    ipv6_network = ip_network(f'{ipv6_prefix}/{ipv6_len}')

                    # ipv6_address情報を取り出してip_interfaceオブジェクトを作成する
                    ipv6_address = intf_data.get('ipv6_address')
                    ipv6_interface = ip_interface(f'{ipv6_address}/{ipv6_len}')

                    # このインタフェースアドレスがプレフィクスの範囲内に入っているか？
                    try:
                        assert ipv6_interface.network == ipv6_network
                    except AssertionError:
                        logger.error(f'{ipv6_interface} is not in {ipv6_network}')

                    # peer
                    peer = intf_data.get('peer')
                    if peer:

                        peer_ifname = peer.get('ifname')
                        _peer_intf_name, peer_intf_number = split_intf_name_and_number(peer_ifname)

                        peer_ipv4_address = peer.get('ipv4_address')
                        peer_ipv4_interface = ip_interface(f'{peer_ipv4_address}/{ipv4_mask}')
                        try:
                            assert peer_ipv4_interface.network == ipv4_network
                        except AssertionError:
                            logger.error(f'{peer_ipv4_interface} is not in {ipv4_network}')

                        is_upstream = intf_data.get('is_upstream')

                        if is_upstream:
                            try:
                                assert ipv4_interface.ip < peer_ipv4_interface.ip
                            except AssertionError:
                                logger.error(f'{ipv4_interface.ip} should be lower than {peer_ipv4_interface.ip}')
                        else:
                            try:
                                assert ipv4_interface.ip > peer_ipv4_interface.ip
                            except AssertionError:
                                logger.error(f'{ipv4_interface.ip} should be larger than {peer_ipv4_interface.ip}')

                        peer_ipv6_address = peer.get('ipv6_address')
                        peer_ipv6_interface = ip_interface(f'{peer_ipv6_address}/{ipv6_len}')
                        try:
                            assert peer_ipv6_interface.network == ipv6_network
                        except AssertionError:
                            logger.error(f'{peer_ipv6_interface} is not in {ipv6_network}')

                        if is_upstream:
                            try:
                                assert ipv6_interface.ip < peer_ipv6_interface.ip
                            except AssertionError:
                                logger.error(f'{ipv6_interface.ip} should be lower than {peer_ipv6_interface.ip}')
                        else:
                            try:
                                assert ipv6_interface.ip > peer_ipv6_interface.ip
                            except AssertionError:
                                logger.error(f'{ipv6_interface.ip} should be larger than {peer_ipv6_interface.ip}')


        except SchemaError as e:
            logger.error('Validation failed!')
            logger.error(f'{str(e)}')
            return 1

        logger.info('Dict Validation success! 👍')

        return 0

    # 実行
    sys.exit(main())
