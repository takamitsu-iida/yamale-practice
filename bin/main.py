#!/usr/bin/env python

import logging
import os
import sys

import yamale



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

#
# ここからスクリプト
#
if __name__ == '__main__':

  def main():

    schema_path = os.path.join(data_dir, 'schema.yaml')
    schema = yamale.make_schema(schema_path)

    data_path = os.path.join(data_dir, 'data.yaml')
    data = yamale.make_data(data_path)

    try:
        yamale.validate(schema, data)
        print('Validation success! 👍')
    except yamale.YamaleError as e:
        logger.error('Validation failed!')
        for result in e.results:
            logger.error(f'Error validating data {result.data} with {result.schema}')
            for error in result.errors:
                logger.error(f'\t{error}')
        return 1

    return 0

  # 実行
  sys.exit(main())
