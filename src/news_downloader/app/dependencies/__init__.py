import hashlib

def str_2_md5(str, salt='articles'):
    md5 = hashlib.md5()
    md5.update((salt+str).encode('utf-8'))
    return md5.hexdigest()
