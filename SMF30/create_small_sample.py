"""Create a small sample from dumpsample.bin for faster testing"""

# Read first 100KB of dumpsample.bin
with open('dumpsample.bin', 'rb') as f:
    data = f.read(100000)  # First 100KB only

# Write to small sample
with open('dumpsample_small.bin', 'wb') as f:
    f.write(data)

print(f"Created dumpsample_small.bin: {len(data):,} bytes")
print("This should parse much faster in the notebook!")
