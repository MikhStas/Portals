#!/usr/bin/python3

import argparse
import platform
import sys
import re
import os
import subprocess

RAMDISK_CODE = '0dT246^7FzZF'
RAMDISK_NAME = '.ramid'

def create_menu(parser_obj):
    subparsers = parser_obj.add_subparsers(title='Commands',
                                       description='Valid commands:',
                                       help='Description' )

    create_cmd_parser = subparsers.add_parser('create', help='Create ramdisk')
    create_cmd_parser.add_argument('-p', dest='path', default='/mnt/HighwayToRAM', 
                                  help='Path to mount point (/mnt/HighwayToRAM default)')
    create_cmd_parser.add_argument('-s', dest='size', default='512M', help='Ramdisk size (512M (default), 1G, etc)')
    create_cmd_parser.set_defaults(func=create_highway)

    close_cmd_parser = subparsers.add_parser('close', help='Remove ramdisk')
    close_cmd_parser.add_argument('-p', dest='path', default='/mnt/HighwayToRAM', help='Path to mount point')
    close_cmd_parser.set_defaults(func=close_highway)

    clear_cmd_parser = subparsers.add_parser('clear', help='Clear ramdisk')
    clear_cmd_parser.add_argument('-p', dest='path', default='/mnt/HighwayToRAM', help='Path to mount point')
    clear_cmd_parser.set_defaults(func=clear_highway)

def create_highway(args):
    '''
    Creates ramdisk with given size and path
    '''

    print('Creating highway...')

    path = args.path
    size = args.size
    perm = '777'

    sub_check_root()

    try:
        if sub_check_free_mem(size):
            sub_check_create_dir(path)
            subprocess.run(['mount', '-t', 'ramfs', '-o', f'size={size}', 'ramfs', path], check=True)
            create_check_ramid('create', path)
            sub_set_dir_perm(path, perm)
    except subprocess.CalledProcessError as e:
        print('!!! An error raises when mounting ramdisk !!!')
    except Exception as e:
        print('!!! An error raises when creating highway !!!')
        print(f'--> {e}')
    else:
        print(f'{size} ramdisk successfully mounted on {path}!')

def clear_highway(args):
    '''
    Clears ramdisk directory (skips hidden files)
    '''
    path = sub_remove_slash(args.path)
    print(f'Clearing {path}...')

    create_check_ramid('check', path)
    if os.listdir(path) == ['.ramid']:
        print(f'{path} is already empty!')
    else:
        try:
            shell_cmd = f'rm -r {path}/*'
            subprocess.run(shell_cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f'!!! An error raises when clearing highway {path} !!!')
        else:
            print(f'{path} successfully cleared!')

def close_highway(args):
    '''
    Closes ramdisk and remove one's directory
    '''
    sub_check_root()
    print('Closing highway...')

    path = args.path

    create_check_ramid('check', path)
    try:
        subprocess.run(['umount', path], check=True)
    except subprocess.CalledProcessError as e:
        print(f'!!! An error raises when unmounting highway {path}')
    else:
        print(f'--> Highway {path} successfully unmounted!')

    sub_check_remove_dir(path)
    print(f'--> Highway {path} successfully removed')

def create_check_ramid(action, path):
    '''
    Identifies highway ramdisk with file .ramid with string code. Using this code checks if given directory is highway
    '''
    ramdisk_code = '0dT246^7FzZF'
    ramdisk_name = '.ramid'
    ramid_path = os.path.join(path, ramdisk_name)

    if action == 'create':
        with open(ramid_path, 'w') as ramid_obj:
            ramid_obj.write(RAMDISK_CODE)
            print(f'--> Created {ramid_path} file')
    elif action == 'check':
        if os.path.isfile(ramid_path):
            with open(ramid_path, 'r') as ramid_obj:
                code = ramid_obj.read()
                if code == ramdisk_code:
                    print('--> Highway successfully approved')
                else:
                    sys.exit('!!! Ramdisk signature is corrupted !!!')
        else:
            sys.exit(f'!!! {ramid_path} not found! Is this highway directory? !!!')
        
def sub_check_root() -> None:
    '''
    Checks this programm has a root permissions
    '''
    if os.geteuid() != 0:
        sys.exit('!!! You need root permissions to do this !!!')

def sub_remove_slash(string: str) -> str:
    if string[-1] == '/':
        return string[:-1]
    else:
        return string

def sub_check_create_dir(path: str) -> None:
    '''
    Checks if the directory given by path exists and creates it if necessary
    '''
    if isinstance(path, str) and path != '':
        if os.path.exists(path):
            if os.path.isdir(path):
                print(f'--> Directory {path} already exists!')
            else:
                raise ValueError('!!! This path is already used !!!')
        else:
            os.mkdir(path)
            print(f'--> Directory {path} created')
    else:
        raise ValueError('!!! Path is empty or has a wrong type !!!')

def sub_check_remove_dir(path:str) -> None:
    if isinstance(path, str) and path != '':
        if os.path.exists(path) and os.path.isdir(path):
            os.rmdir(path)
        else:
            print(f'--> Directory {path} does not exist!')
    else:
        raise ValueError('!!! Path is empty or has a wrong type !!!') 

def sub_set_dir_perm(path: str, perm: str) -> None:
    'Applies the given permissions to the directory. Permission must be "777" format'
    perm_pattern = r'^[0-7][0-7][0-7]$'

    if re.match(perm_pattern, perm):
        if isinstance(path, str) and path != '':
            if os.path.exists(path) and os.path.isdir(path):
                subprocess.call(['chmod', perm, path])
                print(f'--> {path} permission changed to {perm}')
            else:
                print(f'--> Directory {path} does nor exist!')
        else:
            raise ValueError('!!! Path is empty or has a wrong type !!!')
    else:
        raise ValueError('!!! Permissions has wrong format !!!')

def sub_check_free_mem(size: str) -> bool:
    '''
    Checks available memory equal or bigger size
    '''
    required_mem_kB = sub_size_to_kB(size)
    free_mem_kB = None
    result = False
   
    try: 
        with open('/proc/meminfo') as meminfo:
            for line in meminfo:
                if 'MemAvailable' in line:
                    free_mem_kB = int(line.split()[1])
                    break
    except Exception as e:
        print('!!! An error raises during reading /proc/meminfo !!!')
        print(f'-->{e}')

    if required_mem_kB > free_mem_kB:
        print("!!! It's not enough free memory !!!")
    else:
        print(f'--> {size} memory can be allocated')
        result = True
    
    return result

def sub_size_to_kB(size: str) -> int:
    '''
    Checks if size string correct and convert size to kB
    '''
    result = 0

    pattern = r'^(\d+)([kMG])$'
    match_obj = re.match(pattern, size)
    if match_obj:
        digits = match_obj.group(1)
        unit_prefix = match_obj.group(2)
        if unit_prefix == 'k':
            result = int(digits)
        elif unit_prefix == 'M':
            result = int(digits) * 1024
        elif unit_prefix == 'G':
            result = int(digits) * 1024 * 1024
    else:
        raise ValueError('Size string have incorrect format!')

    return result

def sub_check_os() -> None:
    '''
    Checks the OS type, if one not Linux print message and exit
    '''
    if platform.system() != 'Linux':
        print('This program cat be used only with Linux. Bye')
        sys.exit()

def main_func():
    sub_check_os()

    parser = argparse.ArgumentParser(description='Ramdisk manager')
    create_menu(parser)
    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)    

if __name__ == '__main__':
    main_func()
