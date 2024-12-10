import math
from geopy.distance import geodesic
import argparse
import sys

# 1. 定数と文字セットの定義
CHARSET = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
    'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R',
    'T', 'U', 'V', 'W', 'X', 'Y', '2', '3',
    '4', '6', '7', '8', '9'
]

BASE = len(CHARSET)  # 29

# マッピング辞書の作成
CHAR_TO_INDEX = {char: idx for idx, char in enumerate(CHARSET)}
INDEX_TO_CHAR = {idx: char for idx, char in enumerate(CHARSET)}

def int_to_base29(n, length=5):
    """整数を指定された長さのBase29文字列に変換します。"""
    chars = []
    for _ in range(length):
        chars.append(INDEX_TO_CHAR[n % BASE])
        n = n // BASE
    return ''.join(reversed(chars))

def base29_to_int(s):
    """Base29文字列を整数に変換します。"""
    n = 0
    for char in s:
        if char not in CHAR_TO_INDEX:
            raise ValueError(f"無効な文字 '{char}' が含まれています。")
        n = n * BASE + CHAR_TO_INDEX[char]
    return n

def encode(lat, lon):
    """
    緯度と経度を10文字のコードにエンコードします。

    Parameters:
        lat (float): 緯度（-90から+90）
        lon (float): 経度（-180から+180）

    Returns:
        str: 10文字のコード
    """
    # バリデーション
    if not (-90 <= lat <= 90):
        raise ValueError("緯度は -90 から +90 の範囲でなければなりません。")
    if not (-180 <= lon <= 180):
        raise ValueError("経度は -180 から +180 の範囲でなければなりません。")

    # 正規化
    lat_norm = (lat + 90) / 180  # 0から1
    lon_norm = (lon + 180) / 360  # 0から1

    # 24ビットの整数に変換
    lat_int = int(math.floor(lat_norm * (2**24 - 1)))
    lon_int = int(math.floor(lon_norm * (2**24 - 1)))

    # Base29に変換
    lat_code = int_to_base29(lat_int, length=5)
    lon_code = int_to_base29(lon_int, length=5)

    return lat_code + lon_code

def decode(code):
    """
    10文字のコードを緯度と経度にデコードします。

    Parameters:
        code (str): 10文字のコード

    Returns:
        tuple: (緯度, 経度)
    """
    if len(code) != 10:
        raise ValueError("コードは10文字でなければなりません。")

    lat_code = code[:5]
    lon_code = code[5:]

    # Base29から整数に変換
    lat_int = base29_to_int(lat_code)
    lon_int = base29_to_int(lon_code)

    # 正規化を元に戻す
    lat_norm = lat_int / (2**24 - 1)
    lon_norm = lon_int / (2**24 - 1)

    # 緯度と経度を計算
    lat = lat_norm * 180 - 90
    lon = lon_norm * 360 - 180

    return (lat, lon)

def calculate_error(lat, lon):
    """
    緯度と経度の座標に基づいて、エンコード・デコード後の誤差を計算します。

    Parameters:
        lat (float): 元の緯度
        lon (float): 元の経度

    Returns:
        float: 誤差（メートル）
    """

    code = encode(lat, lon)
    decoded_lat, decoded_lon = decode(code)

    original = (lat, lon)
    decoded = (decoded_lat, decoded_lon)

    return geodesic(original, decoded).meters

def main():
    parser = argparse.ArgumentParser(
        description="NewCode-Geo Command Line Tool"
    )
    subparsers = parser.add_subparsers(dest='command', help='Select Mode')

    # エンコード用サブコマンド
    encode_parser = subparsers.add_parser('encode', help='Encode')
    encode_parser.add_argument('latitude', type=float, help='Latitude')
    encode_parser.add_argument('longitude', type=float, help='Longitude')

    # デコード用サブコマンド
    decode_parser = subparsers.add_parser('decode', help='Decode')
    decode_parser.add_argument('code', type=str, help='NewCode-Geo')

    args = parser.parse_args()

    if args.command == 'encode':
        try:
            code = encode(args.latitude, args.longitude)
            print(f"Encoded Code: {code}")
            error = calculate_error(args.latitude, args.longitude)
            print(f"Error: {error:.2f} Metor(s)")
        except ValueError as ve:
            print(f"Error: {ve}")
            sys.exit(1)
    elif args.command == 'decode':
        try:
            lat, lon = decode(args.code)
            print(f"Decoded Coordinates:")
            print(f"Lat: {lat}")
            print(f"Lon: {lon}")
        except ValueError as ve:
            print(f"Error: {ve}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

# 3. 使用例
if __name__ == "__main__":
    main()
