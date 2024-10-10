# Initial register
registro = 0b00011001  # Example: 0xAC in binary
# Define lsb and msb
lsb = 5  # Least significant bit
msb = 7  # Most significant bit
# Calculate the number of iterations
n_iterations = msb - lsb + 1
# Create the mask for the range between lsb and msb
mask = 0
for i in range(lsb, msb + 1):
    mask |= (1 << i)  # Set the bits between lsb and msb to 1
# Keep the bits outside the range (we save them to restore them later)
external_bits = registro & ~mask
# Loop to increment the internal bits
for increment in range(1 << n_iterations):  # Loop from 0 to 2^(msb-lsb+1) - 1
    # Operation on the internal bits (increment)
    internal_bits = (increment << lsb) & mask  # Apply the increment and limit it to the mask
    print(bin(internal_bits))
    # Combine the external bits with the modified internal bits
    modified_register = external_bits | internal_bits
    print(bin(modified_register))
    # Print the results for each iteration
    print(f"Iteration {increment}: Modified register = {modified_register:#04x}")


