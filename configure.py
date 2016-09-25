import yaml

config_dir = "config"

def main():
    parse()

def parse():
    try:
        left_index = int(raw_input('Enter index of left camera: '))
    except ValueError:
        print "Please enter a number."

    try:
        right_index = int(raw_input('Enter index of right camer: '))
    except ValueError:
        print "Please enter a number."

    source_dir = raw_input('Enter full path to image source directory: ')
    dest_dir = raw_input('Enter full path to image output directory: ')
    key_frame = raw_input('Enter full path to key frame image: ')

    try:
        width = int(raw_input('Enter image width: '))
    except ValueError:
        print "Please enter a number."

    format = raw_input('Enter image format: ')

    settings = {
            'left-index': left_index,
            'right-index': right_index,
            'source-dir': source_dir,
            'dest-dir': dest_dir,
            'key-frame': key_frame,
            'width': width,
            'format': format
            }
    with open(config_dir + '/profile.yml', 'w') as file:
        yaml.dump(settings, file, default_flow_style=False)

if __name__ == "__main__":
    main()