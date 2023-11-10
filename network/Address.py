from ipaddress import IPv4Address


class Address:
    def __init__(self, ip: any, port: int) -> None:
        try:
            self.ip = IPv4Address(ip)
        except ValueError:
            raise Exception('Invalid IPv4', ip)

        self.port = port

    def to_json(self):
        return {
            "ipv4": self.ip.compressed,
            "port": self.port
        }

    @staticmethod
    def from_json(raw_json):
        ip = raw_json['ipv4']
        port = raw_json['port']
        return Address(ip, port)

    @property
    def addr(self):
        return (self.ip.compressed, self.port)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Address):
            raise ValueError(f'Expected Address, got {type(__value)}')
        return self.addr == __value.addr
