from socket import *
import struct
import argparse
import json
import time
import hashlib

# Const Value
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN, OP_ERROR = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN', "ERROR"
TYPE_FILE, TYPE_DATA, TYPE_AUTH, DIR_EARTH = 'FILE', 'DATA', 'AUTH', 'EARTH'
FIELD_OPERATION, FIELD_DIRECTION, FIELD_TYPE, FIELD_USERNAME, FIELD_PASSWORD, FIELD_TOKEN = 'operation', 'direction', 'type', 'username', 'password', 'token'
FIELD_KEY, FIELD_SIZE, FIELD_TOTAL_BLOCK, FIELD_MD5, FIELD_BLOCK_SIZE = 'key', 'size', 'total_block', 'md5', 'block_size'
FIELD_STATUS, FIELD_STATUS_MSG, FIELD_BLOCK_INDEX = 'status', 'status_msg', 'block_index'
DIR_REQUEST, DIR_RESPONSE = 'REQUEST', 'RESPONSE'


def _argparse():
    parse = argparse.ArgumentParser()
    parse.add_argument("-server_ip", default='', action='store', required=False, dest="server_ip",
                       help="The IP address bind to the server. Default bind all IP.")
    parse.add_argument("-id", default='2034590', action='store', required=False, dest="id",
                       help="The port that server listen on. Default is 1379.")
    parse.add_argument("-f", default='', action='store', required=False, dest="file",
                       help="The file for server.")
    return parse.parse_args()


def make_packet(json_data, bin_data=None):
    j = json.dumps(dict(json_data), ensure_ascii=False)
    j_len = len(j)
    if bin_data is None:
        return struct.pack('!II', j_len, 0) + j.encode()
    else:
        return struct.pack('!II', j_len, len(bin_data)) + j.encode() + bin_data


def make_request_packet(data_type, operation, username, token, json_data, bin_data=None):
    json_data[FIELD_TYPE] = data_type
    json_data[FIELD_OPERATION] = operation
    json_data[FIELD_DIRECTION] = DIR_REQUEST
    json_data[FIELD_USERNAME] = username
    json_data[FIELD_PASSWORD] = hashlib.md5(json_data[FIELD_USERNAME].encode()).hexdigest().lower()
    json_data[FIELD_TOKEN] = token
    json_data[FIELD_SIZE] = len(bin_data)
    json_data[FIELD_KEY] = "test"
    json_data[FIELD_BLOCK_INDEX] = 0

    return make_packet(json_data, bin_data)


def get_tcp_packet(conn):
    # 1. get length of json_data and length of bin_data
    bin_data = b''
    while len(bin_data) < 8:
        data_rec = conn.recv(8)  # 8 bytes
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    data = bin_data[:8]  # 0-7
    bin_data = bin_data[8:]  # 8-end, clear list
    j_len, b_len = struct.unpack('!II', data)

    # 2. get json_data
    while len(bin_data) < j_len:
        data_rec = conn.recv(j_len)
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    j_bin = bin_data[:j_len]

    try:
        json_data = json.loads(j_bin.decode())
    except Exception as ex:
        return None, None

    # 3. get bin_data
    bin_data = bin_data[j_len:]  # clear list
    while len(bin_data) < b_len:
        data_rec = conn.recv(b_len)
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    return json_data, bin_data


def tcp_client(server_ip, server_port, file):
    tcp_addr = (server_ip, server_port)
    client_socket = socket(AF_INET, SOCK_STREAM)  # TCP
    client_socket.connect(tcp_addr)

    json_data_send: dict = {}
    json_data_send[FIELD_TYPE] = TYPE_AUTH
    json_data_send[FIELD_OPERATION] = OP_LOGIN
    json_data_send[FIELD_DIRECTION] = DIR_REQUEST
    json_data_send[FIELD_USERNAME] = "Zhen.Ma20"
    json_data_send[FIELD_PASSWORD] = hashlib.md5(json_data_send[FIELD_USERNAME].encode()).hexdigest().lower()

    # client_socket.send(make_request_packet(TYPE_AUTH, OP_LOGIN, "Zhen.Ma20", token, {}, file_data))
    client_socket.send(make_packet(json_data_send))
    json_data_recv, bin_data = get_tcp_packet(client_socket)
    token = json_data_recv[FIELD_TOKEN]
    print(f'Token: {token}')

    json_data_send[FIELD_TYPE] = TYPE_FILE
    json_data_send[FIELD_OPERATION] = OP_SAVE
    json_data_send[FIELD_DIRECTION] = DIR_REQUEST
    json_data_send[FIELD_TOKEN] = token
    json_data_send[FIELD_KEY] = "file.bin"
    json_data_send[FIELD_SIZE] = len(open(file, 'rb').read())
    client_socket.send(make_packet(json_data_send))

    block_index = 0
    with open(file, 'rb') as f:
        while True:
            file_data = f.read(20480)
            if not file_data:
                break
            json_data_send[FIELD_OPERATION] = OP_UPLOAD
            json_data_send[FIELD_DIRECTION] = DIR_REQUEST
            json_data_send[FIELD_TOKEN] = token
            json_data_send[FIELD_KEY] = "file.bin"
            json_data_send[FIELD_SIZE] = len(file_data)
            json_data_send[FIELD_BLOCK_INDEX] = block_index
            block_index += 1
            client_socket.send(make_packet(json_data_send, file_data))
            json_data_recv, bin_data = get_tcp_packet(client_socket)
            print(json_data_recv)

    client_socket.close()


def main():
    parser = _argparse()
    server_ip = parser.server_ip
    file = parser.file
    server_port = 1379

    tcp_client(server_ip, server_port, file)


if __name__ == '__main__':
    main()
