__author__          = 'agsvn'

import struct

class BinaryWriter:
    def __init__(self, file=None):
        self.f = file
        self.bytes = bytearray()

    def __bytes__(self):
        return bytes(self.bytes)

    def WriteInt8(self, value, endian="<"):
        self.pack('%sb' % endian, value)

    def WriteUInt8(self, value, endian="<"):
        self.pack('%sB' % endian, value)

    def WriteInt16(self, value, endian="<"):
        self.pack('%sh' % endian, value)

    def WriteUInt16(self, value, endian="<"):
        self.pack('%sH' % endian, value)

    def WriteInt32(self, value, endian="<"):
        self.pack('%si' % endian, value)

    def WriteUInt32(self, value, endian="<"):
        self.pack('%sI' % endian, value)

    def WriteInt64(self, value, endian="<"):
        self.pack('%sq' % endian, value)

    def WriteUInt64(self, value, endian="<"):
        self.pack('%sQ' % endian, value)

    def WriteFloat(self, value, endian="<"):
        self.pack('%sf' % endian, value)

    def WriteDouble(self, value, endian="<"):
        self.pack('%sd' % endian, value)
    
    def WriteBool(self, value):
        self.pack('?', value)

    def WriteByte(self, value):
        self.pack('B', value)

    def WriteBytes(self, value):
        if self.f:
            self.f.write(value)
        self.bytes.extend(value)

    def WriteString(self, value):
        self.WriteUInt16(len(value))
        self.WriteBytes(value.encode())

    def pack(self, fmt, value):
        if self.f:
            self.f.write(struct.pack(fmt, value))

        # pack bytes into bytes array
        self.bytes.extend(struct.pack(fmt, value))

class BinaryReader:
    def __init__(self, file):
        self.f = file

    def ReadInt8(self, endian="<"):
        return struct.unpack('%sb' % endian, self.f.read(1))[0]

    def ReadUInt8(self, endian="<"):
        return struct.unpack('%sB' % endian, self.f.read(1))[0]

    def ReadInt16(self, endian="<"):
        return struct.unpack('%sh' % endian, self.f.read(2))[0]

    def ReadUInt16(self, endian="<"):
        return struct.unpack('%sH' % endian, self.f.read(2))[0]

    def ReadInt32(self, endian="<"):
        return struct.unpack('%si' % endian, self.f.read(4))[0]

    def ReadUInt32(self, endian="<"):
        return struct.unpack('%sI' % endian, self.f.read(4))[0]

    def ReadInt64(self, endian="<"):
        return struct.unpack('%sq' % endian, self.f.read(8))[0]

    def ReadUInt64(self, endian="<"):
        return struct.unpack('%sQ' % endian, self.f.read(8))[0]

    def ReadFloat(self, endian="<"):
        return struct.unpack('%sf' % endian, self.f.read(4))[0]

    def ReadDouble(self, endian="<"):
        return struct.unpack('%sd' % endian, self.f.read(8))[0]

    def ReadBool(self):
        return struct.unpack('?', self.f.read(1))[0]

    def ReadByte(self):
        return struct.unpack('B', self.f.read(1))[0]

    def ReadBytes(self, count):
        return self.f.read(count)

    def ReadString(self):
        length = self.ReadUInt16()
        return self.f.read(length).decode()
