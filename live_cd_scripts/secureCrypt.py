import pyAesCrypt


def cryptResult(file):

    # Crypt file
    bufferSize = 64 * 1024
    password = 'applepy'
    pyAesCrypt.encryptFile(
        file, file+".aes", password, bufferSize)


def decryptResult(file):

    # Decrypt file
    bufferSize = 64 * 1024
    password = 'applepy'
    pyAesCrypt.decryptFile(file, file+".json", password, bufferSize)
