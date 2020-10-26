import platform
import os
from OpenSSL import crypto, SSL


on_macos = platform.uname().system.lower() == 'darwin'
on_windows = platform.uname().system.lower() == 'windows'
on_linux = platform.uname().system.lower() == 'linux'
on_wsl = on_linux and "microsoft" in platform.uname().release.lower()


def is_supported():
    return not on_windows


def is_tunnel_needed():
    return on_macos or on_wsl


def create_cache_folder():
    if not os.path.exists('.cache'):
        os.mkdir('.cache')

    if not os.path.isdir('.cache'):
        os.unlink('.cache')
        os.mkdir('.cache')


def read_cache(item):
    create_cache_folder()

    if not os.path.exists(f'.cache/{item}'):
        return None

    return open(f'.cache/{item}', 'r').read()


def write_cache(item, value):
    create_cache_folder()

    return open(f'.cache/{item}', 'w').write(value)


def is_super_user():
    return os.geteuid() == 0


def generate_certificate(
    tld=None,
    cert_file='/dev/null',
    key_file='/dev/null'
):
    if not tld:
        raise('No top level domain informed')

    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    cert = crypto.X509()
    # cert.get_subject().C = countryName
    # cert.get_subject().ST = stateOrProvinceName
    # cert.get_subject().L = localityName
    # cert.get_subject().O = organizationName
    # cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = f'*.{tld}'
    # cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(3600 * 24 * 365 * 10)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(
            crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


def check_if_installed():
    return os.path.exists('.cache/INSTALLED')


def remove_dir(base_path):
    for filename in base_path:
        file_path = os.path.join(base_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root, d) for d in dirs]:
            os.chmod(dir, mode)
    for file in [os.path.join(root, f) for f in files]:
        os.chmod(file, mode)


def change_owner_recursive(path, uid, gid=None):
    if not gid:
        gid = uid
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root, d) for d in dirs]:
            os.chown(dir, uid, gid)
    for file in [os.path.join(root, f) for f in files]:
        os.chown(file, uid, gid)
