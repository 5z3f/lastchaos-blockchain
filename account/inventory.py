__author__          = 'agsvn'

import json

from lib.binary import BinaryWriter

class item:
    def __init__(self, id, uuid, source):
        self.id = id
        self.uuid = uuid
        self.source = source

    def __str__(self):
        return f"{ self.id }:{ self.uuid }:{ json.dumps(self.source) }"

    def __bytes__(self):
        bw = BinaryWriter()
        bw.WriteInt32(self.id)
        bw.WriteString(self.uuid)
        bw.WriteString(self.source['type'])
        bw.WriteInt32(self.source['id'])
        bw.WriteInt32(self.source['localization']['zone'])
        bw.WriteInt32(self.source['localization']['x'])
        bw.WriteInt32(self.source['localization']['y'])
        bw.WriteInt64(self.source['timestamp'])
        return bytes(bw)
        
    @staticmethod
    def read(br):
        id = br.ReadInt32()
        uuid = br.ReadString()
        source = {
            'type': br.ReadString(),
            'id': br.ReadInt32(),
            'localization': {
                'zone': br.ReadInt32(),
                'x': br.ReadInt32(),
                'y': br.ReadInt32()
            },
            'timestamp': br.ReadInt64()
        }
        return item(id, uuid, source)

    def dictify(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'source': self.source
        }