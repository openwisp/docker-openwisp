import ctypes
import socket
from urllib.parse import urlsplit


class UwsgiPacketHeader(ctypes.Structure):
    """Represents the uWSGI packet header structure.

    This structure contains three fields:

    - modifier1: An 8-bit modifier.
    - datasize: A 16-bit data size.
    - modifier2: An 8-bit modifier.
    """

    _pack_ = 1
    _fields_ = [
        ("modifier1", ctypes.c_int8),
        ("datasize", ctypes.c_int16),
        ("modifier2", ctypes.c_int8),
    ]


class UwsgiVar(object):
    """Represents a uWSGI variable structure.

    This structure contains four fields:

    - key_size: A 16-bit size of the key.
    - key: A key of size `key_size`.
    - val_size: A 16-bit size of the value.
    - val: A value of size `val_size`.
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
        """Create a UwsgiVar instance from a buffer.

        Parameters:

        - buffer (bytes): The buffer containing the uWSGI variable data.
        - offset (int, optional): The offset in the buffer where the
        - data starts. Defaults to 0.

        Returns:

        - UwsgiVar: The uWSGI variable instance.
        """
        key_size = ctypes.c_int16.from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_int16)
        key = (ctypes.c_char * key_size).from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_char * key_size)
        val_size = ctypes.c_int16.from_buffer(buffer, offset).value
        offset += ctypes.sizeof(ctypes.c_int16)
        val = (ctypes.c_char * val_size).from_buffer(buffer, offset).value

        return cls(key_size, key, val_size, val)


def pack_uwsgi_vars(var):
    """Pack a dictionary of variables into a uWSGI packet format.

    Parameters:

    - var (dict): The dictionary containing key-value pairs.

    Returns:

    - bytes: The packed uWSGI packet.
    """
    encoded_vars = [(k.encode('utf-8'), v.encode('utf-8')) for k, v in var.items()]
    packed_vars = b''.join(
        bytes(UwsgiVar(len(k), k, len(v), v)) for k, v in encoded_vars
    )
    packet_header = bytes(UwsgiPacketHeader(0, len(packed_vars), 0))
    return packet_header + packed_vars


def parse_addr(addr, default_port=3030):
    """Parse an address string or tuple into a host and port.

    Parameters:

    - addr (str, list, tuple, or set): The address to parse.
    - default_port (int, optional): The default port to use if none is
    - provided. Defaults to 3030.

    Returns:

    - tuple: A tuple containing the host and port.
    """
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
    """Extract the host from a URL.

    Parameters:

    - url (str): The URL string.

    Returns:

    - tuple: A tuple containing the host and the remaining URL path.
    """
    url = url.split('://')[-1]

    if url and url[0] != '/':
        host, _, url = url.partition('/')
        return (host, f'/{url}')

    return '', url


def ask_uwsgi(uwsgi_addr, var, body='', timeout=0, udp=False):
    """Send a request to a uWSGI server and receive the response.

    Parameters:

    - uwsgi_addr (str or tuple): The uWSGI server address. var (dict):
    - The dictionary of uWSGI variables. body (str, optional): The body
    - of the request. Defaults to ''. timeout (int, optional): The
    - timeout for the request. Defaults to 0. udp (bool, optional):
    - Whether to use UDP. Defaults to False.

    Returns:

    - str: The response from the uWSGI server.
    """
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


def uwsgi_curl(uwsgi_addr, method='GET', body='', timeout=0, headers=(), udp=False):
    """Send an HTTP-like request to a uWSGI server.

    Parameters:

    - uwsgi_addr (str): The uWSGI server address. method (str,
    - optional): The HTTP method to use. Defaults to 'GET'. body (str,
    - optional): The body of the request. Defaults to ''. timeout (int,
    - optional): The timeout for the request. Defaults to 0. headers
    - (tuple, optional): Additional headers to include in the request.
    - Defaults to (). udp (bool, optional): Whether to use UDP. Defaults
    - to False.

    Returns:

    - str: The response from the uWSGI server.
    """
    host, uri = get_host_from_url(uwsgi_addr)
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

    result = ask_uwsgi(uwsgi_addr=host, var=var, body=body, timeout=timeout, udp=udp)
    return result
