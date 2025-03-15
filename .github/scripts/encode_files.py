import base64

def encode_file_to_base64(file_path):
    try:
        # Open the binary file in read-binary mode
        with open(file_path, 'rb') as file:
            # Read the binary file and encode it to base64
            encoded_data = base64.b64encode(file.read())
            
            # Convert the bytes to a string (base64 is typically stored as a string)
            encoded_string = encoded_data.decode('utf-8')
            
            return encoded_string
    except Exception as e:
        print(f"Error encoding the file: {e}")
        return None
    
def save_base64_to_file(encoded_string, output_file):
    try:
        with open(output_file, 'w') as file:
            file.write(encoded_string)
        print(f"Encoded base64 string saved to {output_file}")
    except Exception as e:
        print(f"Error saving base64 string to file: {e}")




if __name__ == "__main__":
    file_path = 'token.pickle'  # Path to your binary file
    encoded_string = encode_file_to_base64(file_path)
    print(encoded_string)
    save_base64_to_file(encoded_string, 'encoded_file.txt')
    
