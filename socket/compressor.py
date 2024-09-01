"""
NOT VISIBLE TO USER, meant to compress ascii art to a zst binary file
"""

import zstandard as zstd


def compress_and_store_art(
    input_file_path="cola.txt", output_file_path="cola.whatever"
):
    """
    Compress the ASCII art and store it in a binary file using zstandard.
    """
    with open(input_file_path, "rb") as f:
        cola_art = f.read()
        compressor = zstd.ZstdCompressor()
        compressed_art = compressor.compress(cola_art)

    print(f"Original size: {len(cola_art)} bytes")

    with open(output_file_path, "wb") as f:
        f.write(compressed_art)

    # get the compressed size
    print(f"Compressed size: {len(compressed_art)} bytes")
    return cola_art, compressed_art


def decompress(compressed_art, output_file_path="cola_decompressed.txt"):
    """
    Decompress the compressed ASCII art and store it in a text file.
    """
    decompressor = zstd.ZstdDecompressor()
    decompressed_art = decompressor.decompress(compressed_art)

    with open(output_file_path, "wb") as f:
        f.write(decompressed_art)

    print(f"Decompressed size: {len(decompressed_art)} bytes")
    return decompressed_art


def main():
    """
    Run this once to create the compressed binary file
    """
    og, com = compress_and_store_art()

    print(com)
    decom = decompress(com)

    if og == decom:
        print("Decompressed art matches original art.")
    else:
        print("Decompressed art does not match original art.")


if __name__ == "__main__":
    main()
