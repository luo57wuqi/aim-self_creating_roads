import base64
import re
import os

file_path = r'c:\\Users\\admin\\Desktop\\RPA\\skills\\验证码\\得物验证码url\\response.py'
output_dir = r'c:\\Users\\admin\\Desktop\\RPA\\skills\\验证码'
output_path = os.path.join(output_dir, 'background.webp')

try:
    with open(file_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'"bgImage": "([^"]+)"' , content)
    
    if match:
        base64_string = match.group(1)
        # Check if the string contains the data URI prefix
        if ',' in base64_string:
            header, encoded = base64_string.split(',', 1)
        else:
            encoded = base64_string

        image_data = base64.b64decode(encoded)
        
        with open(output_path, 'wb') as img_file:
            img_file.write(image_data)
        print(f'Background image saved as {output_path}')
    else:
        print('No bgImage found in the file.')
except FileNotFoundError:
    print(f'Error: The file {file_path} was not found.')
except Exception as e:
    print(f'An error occurred: {e}')