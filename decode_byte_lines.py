import struct

# Function to read lines from the text file
def read_byte_lines(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

# Function to print byte data in a readable format
def print_byte_data(byte_line):
    for i in range(0, len(byte_line), 16):
        print(f"{i:04x}: {' '.join(f'{b:02x}' for b in byte_line[i:i+16])}")

# Function to decode sections of the byte data
def decode_bytes(byte_line, offset, fmt):
    size = struct.calcsize(fmt)
    end = offset + size
    if end <= len(byte_line):
        return struct.unpack_from(fmt, byte_line, offset)
    return None

# Function to systematically find specific values in byte data
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

# Function to extract all relevant details from the byte data
def extract_details(byte_line):
    # Expected values and formats
    expected_values = {
        'latitude': -31.93,
        'longitude': 115.96,
        'altitude': 54,
        'squawk': 1200,
        'heading_min': 200,
        'heading_max': 220
    }
    formats = ['<d', '<f', '<i', '<h', '<B']  # Adding more formats to the search
    
    details = {}
    
    # Latitude and Longitude found at known offsets
    latitude_offset = 50
    longitude_offset = 41
    altitude_offset = 92
    heading_offset = 72
    
    latitude_found = find_values_in_range(byte_line, [-31.93], latitude_offset - 20, latitude_offset + 20, formats)
    longitude_found = find_values_in_range(byte_line, [115.96], longitude_offset - 20, longitude_offset + 20, formats)
    
    details['latitude'] = latitude_found
    details['longitude'] = longitude_found
    
    # Print byte data for manual inspection
    print("Byte data:")
    print_byte_data(byte_line)
    
    # Manually inspect byte data around known offsets
    print("\nDetailed Inspection around known offsets:")
    for offset in range(latitude_offset - 20, latitude_offset + 20):
        decoded = {fmt: decode_bytes(byte_line, offset, fmt) for fmt in formats}
        print(f"Offset {offset}: {decoded}")
    
    for offset in range(longitude_offset - 20, longitude_offset + 20):
        decoded = {fmt: decode_bytes(byte_line, offset, fmt) for fmt in formats}
        print(f"Offset {offset}: {decoded}")
    
    # Find altitude, squawk, and heading around known offsets
    altitude_found = find_values_in_range(byte_line, [54], altitude_offset - 20, altitude_offset + 20, formats)
    squawk_found = find_values_in_range(byte_line, [1200], 10, 120, formats)
    heading_found = find_values_in_range(byte_line, list(range(200, 221)), heading_offset - 20, heading_offset + 20, formats)
    
    if altitude_found:
        details['altitude'] = altitude_found
        for (offset, fmt, value) in altitude_found:
            print(f"Found altitude {value} with format {fmt} at offset {offset}")
    
    if squawk_found:
        details['squawk'] = squawk_found
        for (offset, fmt, value) in squawk_found:
            print(f"Found squawk {value} with format {fmt} at offset {offset}")
    
    if heading_found:
        details['heading'] = heading_found
        for (offset, fmt, value) in heading_found:
            print(f"Found heading {value} with format {fmt} at offset {offset}")
    
    return details

# Read lines from the text file
filename = 'byte_lines.txt'
byte_lines = read_byte_lines(filename)

# Extract details from each line
for line in byte_lines:
    print("\nDecoding line:")
    print(line)
    byte_line = eval(line)
    details = extract_details(byte_line)
    if details:
        print(f"Extracted details: {details}")
    else:
        print("Expected values not found in this line.")

