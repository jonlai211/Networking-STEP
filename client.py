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


class TCPClient:
    # default values
    __ip = "127.0.0.1"
    __id = "2034590"
    __file = "file.bin"
    __port = 1379

    def __init__(self, parser):
        self.parser = parser
        __ip = parser.server_ip
        __id = parser.id
        __file = parser.file

    def get_tcp_packet(self, conn):
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

    def make_packet(self, json_data, bin_data=None):
        j = json.dumps(dict(json_data), ensure_ascii=False)
        j_len = len(j)
        if bin_data is None:
            return struct.pack('!II', j_len, 0) + j.encode()
        else:
            return struct.pack('!II', j_len, len(bin_data)) + j.encode() + bin_data

    def make_request_packet(self, data_type, operation, json_data, bin_data=None):
        json_data[FIELD_TYPE] = data_type
        json_data[FIELD_OPERATION] = operation
        json_data[FIELD_DIRECTION] = DIR_REQUEST

        return self.make_packet(json_data, bin_data)

    def comm(self, ip=__ip, id=__id, port=__port, file=__file):
        tcp_addr = (ip, port)
        client_socket = socket(AF_INET, SOCK_STREAM)  # TCP
        client_socket.connect(tcp_addr)

        client_socket.send(
            self.make_request_packet(TYPE_AUTH, OP_LOGIN, {
                FIELD_USERNAME: id,
                FIELD_PASSWORD: hashlib.md5(id.encode()).hexdigest().lower()
            })
        )
        json_data_recv, bin_data = self.get_tcp_packet(client_socket)
        token = json_data_recv[FIELD_TOKEN]
        print(f'Token: {json_data_recv[FIELD_TOKEN]}')

        client_socket.send(
            self.make_request_packet(TYPE_FILE, OP_SAVE, {
                FIELD_TOKEN: token,
                FIELD_KEY: file,
                FIELD_SIZE: len(open(file, 'rb').read())
            })
        )
        json_data_recv, bin_data = self.get_tcp_packet(client_socket)
        print(json_data_recv)

        block_index = 0
        with open(file, 'rb') as f:
            while True:
                file_data = f.read(20480)
                if not file_data:
                    break

                client_socket.send(
                    self.make_request_packet(TYPE_FILE, OP_UPLOAD, {
                        FIELD_TOKEN: token,
                        FIELD_KEY: file,
                        FIELD_SIZE: len(file_data),
                        FIELD_BLOCK_INDEX: block_index
                    }, file_data)
                )

                block_index += 1
                json_data_recv, bin_data = self.get_tcp_packet(client_socket)
                print(json_data_recv)

        client_socket.close()


def main():
    parser = _argparse()
    tcp = TCPClient(parser)
    tcp.comm()


if __name__ == '__main__':
    main()
