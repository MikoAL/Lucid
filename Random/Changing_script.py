import os
script_dir = os.path.dirname(os.path.realpath(__file__))

input_file_path = f'{script_dir}\\transcript.txt'
output_file_path = f'{script_dir}\\modified_file.txt'

with open(input_file_path, 'r') as input_file:
    content = input_file.read()

# Add \n before every '-'
modified_content = content.replace(' -', '\n\n-')

with open(output_file_path, 'w') as output_file:
    output_file.write(modified_content)

print(f'Modified content written to {output_file_path}')
