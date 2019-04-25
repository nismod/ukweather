"""Download from CEDA Archive
"""
import configparser
import ftplib
import os


def main():
    """Download climate data - script entry point
    """
    # Read connection details
    if 'CEDA_USERNAME' in os.environ and 'CEDA_PASSWORD' in os.environ:
        ceda_username = os.environ['CEDA_USERNAME']
        ceda_password = os.environ['CEDA_PASSWORD']
    else:
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.path.dirname(__file__), 'ftp.ini'))
        ceda_username = parser['ceda-config']['ceda_username']
        ceda_password = parser['ceda-config']['ceda_password']

    ftp_host = 'ftp.ceda.ac.uk'
    # local_dir = os.path.join(os.path.dirname(__file__), 'cache')
    # remote_base_path = 'badc/ukmo-midas-open/data'
    # remote_base_path = 'badc/weather_at_home/data/marius_time_series'

    conn = ftplib.FTP(ftp_host, user=ceda_username, passwd=ceda_password)
    conn.cwd('badc/weather_at_home/data/marius_time_series')
    listing = find(conn, recursive=True, human=True)
    conn.quit()

    for entry in listing:
        print(entry)


def download(conn, remote_fname, local_fname):
    """Download a single file, using an FTP connection, from remote to local
    """
    with open(local_fname, 'wb') as file_handle:
        conn.retrbinary("RETR {}".format(remote_fname), file_handle.write)


def find(conn, dirname=None, recursive=False, types=None, human=False):
    """Find files/directories in FTP remote location
    """
    # default to current (remote) working directory
    if dirname is None:
        dirname = '.'

    # default to directories and files
    # ftplib.FTP.mlsd type could be ('dir', 'file', 'cdir', 'pdir')
    if types is None:
        types = ('dir', 'file')

    # request listings
    contents = conn.mlsd(dirname, facts=['type', 'size'])

    # format to full relative path
    contents = [
        ("{}/{}".format(dirname, name), details)
        for name, details in contents
    ]

    # format to human-readable size
    if human:
        new_contents = []
        for name, details in contents:
            if 'size' in details:
                details['size'] = human_filesize(details['size'])
            new_contents.append((name, details))
        contents = new_contents

    # find nested directories and recurse
    nested_dirs = [item for item in contents if item[1]['type'] == 'dir']
    if recursive and nested_dirs:
        for nested_dirname, _ in nested_dirs:
            contents.extend(find(conn, nested_dirname, recursive=True))

    # return only requested types
    return filter(lambda item: item['type'] in types, contents)

def human_filesize(filesize):
    """Format a filesize in bytes to human-readable
    """
    for unit in ['', 'KiB', 'MiB', 'GiB', 'TiB']:
        if filesize < 1024:
            break
        filesize = filesize / 1024
    return "{filesize:.3f} {unit}".format(filesize=filesize, unit=unit)
