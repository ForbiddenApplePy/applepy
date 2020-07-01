import os

os.system('lsblk > result.txt')
os.system('mkdir /mnt/disk')


def parse(file_name):
    result = []
    with open(file_name) as input_file:
        for line in input_file:
            temp_arr = line.split(' ')
            for item in temp_arr:
                if '└─' in item or '├─' in item:
                    result.append(item.replace('└─', '').replace('├─', ''))
    return result


drives_list = parse('result.txt')
for drive in drives_list:
    os.system('mount /dev/%s /mnt/disk' % (drive))
    os.system(
        'find /mnt/disk/ -depth -type f -exec shred -v -n 1 -z -u {} \;')
    # os.system('rm -rf ')
