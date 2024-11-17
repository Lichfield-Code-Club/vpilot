import struct

def read_byte_lines(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

def decode_bytes(byte_line, offset, fmt):
    size = struct.calcsize(fmt)
    end = offset + size
    if end <= len(byte_line):
        return struct.unpack_from(fmt, byte_line, offset)
    return None

def find_values_in_range(byte_line, expected_values, start_offset, end_offset, formats):
    found_values = []
    for offset in range(start_offset, end_offset):
        for fmt in formats:
            try:
                value = struct.unpack_from(fmt, byte_line, offset=offset)[0]
                if any(abs(value - expected) < 0.01 for expected in expected_values):
                    found_values.append((offset, fmt, value))
            except struct.error:
                continue
    return found_values

def extract_details(byte_line):
    expected_values = {
        'latitude': -31.93,
        'longitude': 115.96,
        'altitude': 54,
        'heading_min': 200,
        'heading_max': 220
    }
    formats = ['<d', '<f', '<i', '<h', '<B']  
    
    details = {}
    latitude_offset = 50
    longitude_offset = 41
    altitude_offset = 92
    heading_offset = 72
    
    details['latitude'] = find_values_in_range(byte_line, [-31.93], latitude_offset - 20, latitude_offset + 20, formats)
    details['longitude'] = find_values_in_range(byte_line, [115.96], longitude_offset - 20, longitude_offset + 20, formats)
    details['altitude'] = find_values_in_range(byte_line, [54], altitude_offset - 20, altitude_offset + 20, formats)
    details['heading'] = find_values_in_range(byte_line, list(range(200, 221)), heading_offset - 20, heading_offset + 20, formats)
    
    return details

filename = 'byte_lines.txt'
byte_lines = read_byte_lines(filename)

for line in byte_lines:
    byte_line = eval(line)
    details = extract_details(byte_line)
    if details:
        print(f"Extracted details: {details}")
    else:
        print("Expected values not found in this line.")

