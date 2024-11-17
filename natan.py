import os
import ast
import struct

def summary(lines):
    sent_messages = [x for x in lines if x.startswith('Sent ')]
    received_messages = [x for x in lines if x.startswith('Received') and 'EventBusHeartbeat' not in x]
    not_decoded = [x for x in lines if x.startswith('Unable to decode response')]

    print(f'we sent {len(sent_messages)} message. received {len(received_messages)} responses and were unable to decode {len(not_decoded)}')

    return received_messages

def decoder(byte_line):
    formats = [
    '<4s 16s d d f f f f f f f',         # Possible 4-byte header, 16-byte message type, lat/lon doubles, and other floats
    '<4s d d f f f f f f f f f',          # 4-byte header, no message type, doubles for lat/lon, floats for other metrics
    '<4s 12s d d f f f f f f',            # 4-byte header, 12-byte message type, doubles, floats
    '<8s d d f f f f f f f f',            # 8-byte header, lat/lon as doubles, various floats
    '<4s 8s d f f f f f f f f',           # 4-byte header, 8-byte message type, mixed doubles/floats
    '<4s d d d d f f f f f f f',          # 4-byte header, doubles for location and alt, heading, etc.
    '<d d d d f f f f f',                 # No header, all numeric data (location as doubles)
    ]

    decoded = []

    # Attempt to decode using each format, with error handling for mismatches
    for fmt in formats:
        try:
            # Decode data according to the current format
            decoded_data = struct.unpack_from(fmt, byte_line)
            # print(f"Decoded with format {fmt}:")
            decoded.append({"decode": decoded_data,"fmt": fmt})
        except struct.error as e:
            print(f"Failed decoding with format {fmt}: {e}")
    return decoded

def handle_data(messages):
    prefix = 'Received response from Host Mode: '
    prefix_len = len(prefix)

    identifier = 'UserAircraftDataUpdated'

    UserAircraftDataUpdated = {x[prefix_len:] for x in messages if identifier in x and prefix in x}

    for x in UserAircraftDataUpdated:
        # Convert to actual byte data
        byte_line = ast.literal_eval(x)
        decoded_list = decoder(byte_line)
        print(f'{'='*80} {identifier} data {'=' *80}')
        for decoded in decoded_list:
            decode = decoded['decode']
            fmt = decoded['fmt']
            print(f"{'!'*20} FORMAT[{fmt}] {'!'*20}")
            [print(x) for x in decode]


def message_text(messages):
    header = "Received response from Host Mode: b'"
    header_len = len(header)

    # handle_config(messages)
    handle_data(messages)


if __name__ == '__main__':
    sample_message = 'sample.txt'

    with open(sample_message,'r') as fr:
        lines = fr.readlines()

    if len(lines) > 0: 
        messages = summary(lines)
        if len(messages) > 0: message_text(messages)

