import os
import struct


# get file size (bytes)
file_size = os.stat("file.bin")
print(file_size.st_size)
print(bin(file_size.st_size))

# pack it
file_size_bytes = struct.pack('!II', file_size.st_size, 0)
print(file_size_bytes)

# # write it
# file = open("file.bin", "wb")
# file.write(file_size_bytes)
# file.close()

