#!/usr/bin/env python3

""" Python script to implement ACL change on GPFS
    This script adds permissions for Project_DM(Data Managers) group
    Permissions to modify:
      - Permissions on the top directory to allow a group
        to modify/delete any data
    Inherit flag on top directory
      - Allows new subfolders to inherit the ACL permissions
    Permission *not* added:
      - Existing folders/files need to be recursively treated
        to modify ACL
      - Consider using the accompanying shell script for this
    Ideation:
      - If an ACL is provided, use it or else prepare
        it based on the existing acl
      - If a group is provided, use it or else use the group
        from the project
      - A directory is required as an input
    Author BT 2022
"""

import os
import sys
import grp
import subprocess as sp
import argparse as ap
from datetime import datetime as dt


def parse_input():
    print("+ Parsing input")
    #print(dir(ap))
    parser = ap.ArgumentParser(
        description='NFSv4 ACL implementation for GPFS folders')
    parser.add_argument(
        '-d', '--dir', required=True, help='Input Directory to set acl on')
    parser.add_argument(
        '-a', '--aclfile', help='NFSv4 ACL file to implement')
    parser.add_argument(
        '-g', '--group', required=True, help='Group to add the permissions')
    inputArgs = parser.parse_args()
    return inputArgs


def get_acl_gpfs(ipath):
    pass


def run_process(icomm):
    try:
        out = sp.run(icomm, stdout=sp.PIPE, stderr=sp.STDOUT)
    except Exception as e:
        print("Error: running command... exiting \n", e)
        sys.exit()
    return out


def check_group(igroup):
    try:
        out = grp.getgrnam(igroup)
    except Exception as e:
        print(e)
        print("Error: Group %s does not exist ... exiting" % (igroup))
        sys.exit()
    return out


def check_dir(idir):
    try:
        out = os.path.isdir(idir)
    except Exception as e:
        print(e)
        print("Error: Group %s does not exist ... exiting" % (idir))
        sys.exit()
    return out


if __name__ == '__main__':
    print("\n=== \n+ Start main program\n=== \n")

    # Declare globals, date
    idt = dt.now().strftime("%Y-%m-%d")

    # Check input arguments
    inputArgs = parse_input()

    # Check for valid directory
    iDir = inputArgs.dir
    iDirFlg = check_dir(iDir)

    print("\n=== \n+ Check: Valid directory exists\n=== \n",
            iDirFlg)

    # Check for valid group
    iGrp = inputArgs.group
    igroup = check_group(iGrp)
    idirfl = check_dir(iDir)

    # Get current ACL of directory
    com_getaclgpfs = ['/usr/lpp/mmfs/bin/mmgetacl', iDir]
    out_acl = run_process(com_getaclgpfs)

    # Setup ACL files for directory
    d_name = iDir.replace('/', '_')
    in_aclfile = str(iDir)+'/.'+iGrp
    d_acl_file = ('acls/'+d_name+'.acl.dir-'+idt).strip()
    f_acl_file = ('acls/'+d_name+'.acl.file-'+idt).strip()

    print("\n === \n+ Get: Current ACL\n === \n",
            out_acl.stdout.decode("utf-8"))

    # with open(in_aclfile, 'w') as fhi:
    #       print(out_acl.stdout.decode("utf-8") , file=fhi )
    # print(out.stdout)
 
    # Append additional ACL block
    print("\n === \n+ Append: Additional ACL\n===\n")
    print("Written dir ACL file:", d_acl_file)
    print("Written fileACL file:", f_acl_file)

    OwnerPermACL = "(X)READ/LIST (X)WRITE/CREATE (X)APPEND/MKDIR " + \
                   "(X)SYNCHRONIZE (X)READ_ACL (X)READ_ATTR (X)READ_NAMED " + \
                   "(X)DELETE (X)DELETE_CHILD (X)CHOWN " + \
                   "(X)EXEC/SEARCH (X)WRITE_ACL (X)WRITE_ATTR (X)WRITE_NAMED "
 
    add_acl_1 = ["\n",
                 'group:' + iGrp + ':rwxc:allow:FileInherit:DirInherit', "\n",
                 OwnerPermACL, "\n"]

    add_acl_2 = ["\n",
                 'group:' + iGrp + ':rwxc:allow', "\n",
                 OwnerPermACL, "\n"]

    #print('\n Extra dir ACL to be added ', ' '.join(add_acl_1))
    with open(d_acl_file, 'w') as fhd:
        fhd.write(out_acl.stdout.decode("utf-8"))
        for l in add_acl_1:
            fhd.write(l)

    #print('\n Extra file ACL to be added ', ' '.join(add_acl_2))
    with open(f_acl_file, 'w') as fhf:
        fhf.write(out_acl.stdout.decode("utf-8"))
        for l in add_acl_2:
            fhf.write(l)

    # Implement ACL
    print("\n === \n+ Implement: New ACL\n===\n")
    # Modify current ACL of directory
    print("Command to set ACL flags on directory")
    com_putaclgpfs = ['/usr/lpp/mmfs/bin/mmputacl', '-i', d_acl_file, iDir]
    print(' '.join(com_putaclgpfs))

    com_putaclgpfs = ['find -type d', iDir, '|',  'xargs -I {} sh -c',
                     '"/usr/lpp/mmfs/bin/mmputacl -i', d_acl_file, '{}"']
    print(' '.join(com_putaclgpfs))
    print(' ')
    # out_acl = run_process( com_getaclgpfs )

    # Modify current ACL of files
    print("Command to set ACL flags on directory")
    com_putaclgpfs = ['find -not -type d', iDir, '|', 'xargs -I {} sh -c',
                     '"/usr/lpp/mmfs/bin/mmputacl -i', f_acl_file, '{}"']
    print(' '.join(com_putaclgpfs))
    print(' ')
