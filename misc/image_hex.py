"""
This works fine but I decided against including it in the CTF.
There are a lot of magic numbers too ;(
For different picture types and sizes, you should adjust the program.
"""
import random

# Step 1: Open the original  JPEG image in binary mode
with open("img.jpg", "rb") as original_file:
    data = original_file.read()

# step 1.5 EXIF - METADATA DATA 
# find Ducky in ASCII and change to COLAS
ducky = b"Ducky" # goes in all images created by photoshop
cola = b"ColaC"
data = data.replace(ducky, cola)

# find Adobe in ASCII and change to OMP
adobe = b"Adobe" # also as adobe added this to images made in their software
omp = b"ompany"
data = data.replace(adobe, omp)

# Step 2: Cut off the file part of the way through
cutoff_point = len(data) * 98 // 100
truncated_data = data[:cutoff_point]

#  can fill with funnies (as random data)
funnies = (
    "baadf00d",
    "0c0ffee0",
    "abadbabe",
    "00decaf0",
    "00badd11",
    "d0cf11e0",
    "b50db50d",
    "deaddead",
)  

funnies_bytes = []

for funny in funnies:
    if len(funny) % 2 != 0:  # not able to work with hex strings that are not even
        print(funny + " is not even, please add padding ")
    else:
        funnies_bytes.append(bytes.fromhex(funny))

truncated_data = data[:cutoff_point]

for i in range(0, len(data) - cutoff_point, 8):
    if i % 16 == 0:
        truncated_data += b" "  # add some spaces
    else:
        rnd = random.choice(funnies_bytes)
        truncated_data += rnd


# Step 3: Add the hidden message at the end of the truncated file
hidden_text = b"ColaCo{CTFFLAG}"
truncated_data_with_message = (
    truncated_data
    + hidden_text[::-1]
    + truncated_data[len(hidden_text) + 100: len(hidden_text) + 150]
    + b" me reverse"[::-1]
    + b"\xFF\xD9"
)

# Step 4: Write the truncated data to a new JPEG file
with open("truncated.jpg", "wb") as truncated_file:
    truncated_file.write(truncated_data_with_message)
