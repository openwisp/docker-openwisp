import ctypes
import socket
from urllib.parse import urlsplit


class UwsgiPacketHeader(ctypes.Structure):
    """
    struct uwsgi_packet_header {
        uint8_t modifier1;
        uint16_t datasize;
        uint8_t modifier2;
    }
    """

    _pack_ = 1
    _fields_ = [
        ("modifier1", ctypes.c_int8),
        ("datasize", ctypes.c_int16),
        ("modifier2", ctypes.c_int8),
    ]


class UwsgiVar(object):
    """
    struct uwsgi_var {
        uint16_t key_size;
        uint8_t key[key_size];
        uint16_t val_size;
        uint8_t val[val_size];
    }
    """

    def __new__(self, key_size, key, val_size, val):
        class UwsgiVar(ctypes.Structure):
            _pack_ = 1
            _fields_ = [
                ("key_size", ctypes.c_int16),
                ("key", ctypes.c_char * key_size),
                ("val_size", ctypes.c_int16),
                ("val", ctypes.c_char * val_size),
            ]

        return UwsgiVar(key_size, key, val_size, val)

    @classmethod
    def from_buffer(cls, buffer, offset=0):
        key_size = ctypes.c_int16.from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_int16)
        key = (ctypes.c_char * key_size).from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_char * key_size)
        val_size = ctypes.c_int16.from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_int16)
        val = (ctypes.c_char * val_size).from_buffer(buffer, offset).value

        return cls(key_size, key, val_size, val)


def pack_uwsgi_vars(var):
    encoded_vars = [(k.encode('utf-8'), v.encode('utf-8')) for k, v in var.items()]
    packed_vars = b''.join(
        bytes(UwsgiVar(len(k), k, len(v), v)) for k, v in encoded_vars
    )
    packet_header = bytes(UwsgiPacketHeader(0, len(packed_vars), 0))
    return packet_header + packed_vars


def parse_addr(addr, default_port=3030):
    host = None
    port = None
    if isinstance(addr, str):
        if addr.isdigit():
            port = addr
        else:
            parts = urlsplit(f'//{addr}')
            host = parts.hostname
            port = parts.port
    elif isinstance(addr, (list, tuple, set)):
        host, port = addr
    return (host or '127.0.0.1', int(port) if port else default_port)


def get_host_from_url(url):
    url = url.split('://')[-1]

    if url and url[0] != '/':
        host, _, url = url.partition('/')
        return (host, f'/{url}')

    return '', url


def ask_uwsgi(uwsgi_addr, var, body='', timeout=0, udp=False):
    sock_type = socket.SOCK_DGRAM if udp else socket.SOCK_STREAM
    if isinstance(uwsgi_addr, str) and '/' in uwsgi_addr:
        addr = uwsgi_addr
        s = socket.socket(family=socket.AF_UNIX, type=sock_type)
    else:
        addr = parse_addr(addr=uwsgi_addr)
        s = socket.socket(*socket.getaddrinfo(addr[0], addr[1], 0, sock_type)[0][:2])

    if timeout:
        s.settimeout(timeout)

    if body is None:
        body = ''

    s.connect(addr)
    s.send(pack_uwsgi_vars(var) + body.encode('utf8'))
    response = []
    while 1:
        data = s.recv(4096)
        if not data:
            break
        response.append(data)

    s.close()
    return b''.join(response).decode('utf8')


def uwsgi_curl(
    uwsgi_addr, url='localhost', method='GET', body='', timeout=0, headers=(), udp=False
):
    host, uri = get_host_from_url(url)
    parts_uri = urlsplit(uri)

    if '/' not in uwsgi_addr:
        addr = parse_addr(addr=uwsgi_addr)
        if not host:
            host = addr[0]
        port = addr[1]
    else:
        port = None

    var = {
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'PATH_INFO': parts_uri.path,
        'REQUEST_METHOD': method.upper(),
        'REQUEST_URI': uri,
        'QUERY_STRING': parts_uri.query,
        'HTTP_HOST': host,
    }
    for header in headers or ():
        key, _, value = header.partition(':')
        var[f"HTTP_{key.strip().upper().replace('-', '_')}"] = value.strip()
    var['SERVER_NAME'] = var['HTTP_HOST']
    if port:
        var['SERVER_PORT'] = str(port)
    result = ask_uwsgi(
        uwsgi_addr=uwsgi_addr, var=var, body=body, timeout=timeout, udp=udp
    )
    return result
