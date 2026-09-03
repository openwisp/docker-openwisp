from pathlib import Path

ASSETS = {
    "precompressed-static.txt": b"uncompressed static asset",
    "precompressed-static.txt.br": b"\x8b\x0c\x80precompressed Brotli asset\x03",
    "precompressed-static.txt.gz": (
        b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff+(JM\xce\xcf-(J-.N"
        b"MQH\xaf\xca,PH\x042K\x00\xabO\xa0B\x18\x00\x00\x00"
    ),
}


if __name__ == "__main__":
    static_dir = Path("/opt/openwisp/static")
    for filename, content in ASSETS.items():
        static_dir.joinpath(filename).write_bytes(content)
