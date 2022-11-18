import socket
from socket import *
import struct
import argparse
import json
import time
import hashlib

MAX_PACKET_SIZE = 20480

# Const Value
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN, OP_ERROR = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN', "ERROR"
TYPE_FILE, TYPE_DATA, TYPE_AUTH, DIR_EARTH = 'FILE', 'DATA', 'AUTH', 'EARTH'
FIELD_OPERATION, FIELD_DIRECTION, FIELD_TYPE, FIELD_USERNAME, FIELD_PASSWORD, FIELD_TOKEN = 'operation', 'direction', 'type', 'username', 'password', 'token'
FIELD_KEY, FIELD_SIZE, FIELD_TOTAL_BLOCK, FIELD_MD5, FIELD_BLOCK_SIZE = 'key', 'size', 'total_block', 'md5', 'block_size'
FIELD_STATUS, FIELD_STATUS_MSG, FIELD_BLOCK_INDEX = 'status', 'status_msg', 'block_index'
DIR_REQUEST, DIR_RESPONSE = 'REQUEST', 'RESPONSE'


def _argparse():
    parse = argparse.ArgumentParser()
    parse.add_argument("-server_ip", "--server_ip", default='127.0.0.1', action='store', required=False,
                       dest="server_ip",
                       help="The IP address bind to the server. Default bind all IP.")
    parse.add_argument("-port", "--port", default=1379, action='store', required=False, dest="port",
                       help="The port that server listen on. Default is 1379.")
    parse.add_argument("-id", "--id", default='2034590', action='store', required=False, dest="id",
                       help="Your ID")
    parse.add_argument("-f", "--f", default='', action='store', required=False, dest="file",
                       help="The file path. Default is empty (no file will be uploaded)")
    return parse.parse_args()


class TCP_Client:
    def __init__(self, parser):
        self.__ip = parser.server_ip
        self.__id = parser.id
        self.__file = parser.file
        self.__port = parser.port
        self.__client_socket = socket(AF_INET, SOCK_STREAM)
        self.__client_socket.connect((self.__ip, self.__port))

    def __get_packet(self):
        # 1. get length of json_data and length of bin_data
        bin_data = b''
        while len(bin_data) < 8:
            data_rec = self.__client_socket.recv(8)  # 8 bytes
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
            data_rec = self.__client_socket.recv(j_len)
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
            data_rec = self.__client_socket.recv(b_len)
            if data_rec == b'':
                time.sleep(0.01)
            if data_rec == b'':
                return None, None
            bin_data += data_rec
        return json_data, bin_data

    def __make_packet(self, json_data, bin_data=None):
        j = json.dumps(dict(json_data), ensure_ascii=False)
        j_len = len(j)
        if bin_data is None:
            return struct.pack('!II', j_len, 0) + j.encode()
        else:
            return struct.pack('!II', j_len, len(bin_data)) + j.encode() + bin_data

    def __make_request_packet(self, data_type, operation, json_data, bin_data=None):
        json_data[FIELD_TYPE] = data_type
        json_data[FIELD_OPERATION] = operation
        json_data[FIELD_DIRECTION] = DIR_REQUEST

        return self.__make_packet(json_data, bin_data)

    def comm(self):
        try:
            self.__client_socket.send(
                self.__make_request_packet(TYPE_AUTH, OP_LOGIN, {
                    FIELD_USERNAME: self.__id,
                    FIELD_PASSWORD: hashlib.md5(self.__id.encode()).hexdigest().lower()
                })
            )
            json_data_recv, bin_data = self.__get_packet()
            token = json_data_recv[FIELD_TOKEN]
            print(f'Token: {json_data_recv[FIELD_TOKEN]}')

            self.__client_socket.send(
                self.__make_request_packet(TYPE_FILE, OP_SAVE, {
                    FIELD_TOKEN: token,
                    FIELD_KEY: self.__file,
                    FIELD_SIZE: len(open(self.__file, 'rb').read())
                })
            )
            json_data_recv, bin_data = self.__get_packet()
            print(json_data_recv)

        # TODO: MutilThreading
            block_index = 0
            with open(self.__file, 'rb') as f:
                while True:
                    file_data = f.read(MAX_PACKET_SIZE)
                    if not file_data:
                        break

                    self.__client_socket.send(
                        self.__make_request_packet(TYPE_FILE, OP_UPLOAD, {
                            FIELD_TOKEN: token,
                            FIELD_KEY: self.__file,
                            FIELD_SIZE: len(file_data),
                            FIELD_BLOCK_INDEX: block_index
                        }, file_data)
                    )

                    block_index += 1
                    json_data_recv, bin_data = self.__get_packet()
                    print(json_data_recv)

            self.__client_socket.close()
        except socket.error as se:
            print(f'Socket Error: {str(se)}')
        except Exception as e:
            print(f'Socket Error: {str(e)}')
        finally:
            self.__client_socket.close()


def main():
    parser = _argparse()
    tcp_client = TCP_Client(parser)
    tcp_client.comm()


if __name__ == '__main__':
    main()
