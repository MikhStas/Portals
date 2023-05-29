# Portals
A convenient tool for working with ramdisk technology in linux.

The program is designed to work in an OS based on the Linux kernel. When trying to run on other OSS, an error will be displayed.

The program has three options:
- create - creates a new ramdisk in the specified directory and with the specified size. If the directory and size are not specified, then a 512 MB ramdisk is created in the /mnt/Highway To Ram directory. Before creating a ramdisk, the script checks the amount of free RAM. If there is not enough memory, the script generates an error. Permission 777 is set for the created ramdisk.

![Screenshot from 2023-05-29 09-05-23](https://github.com/MikhStas/Portals/assets/61974713/ae93359a-1e78-49d0-83be-eb5cf5876ce1)

- close - deletes the ramdisk and the directory to which it was mounted

![Screenshot from 2023-05-29 09-05-00](https://github.com/MikhStas/Portals/assets/61974713/359ea479-3fa7-4e97-940a-6f1bf5388735)

- clear - deletes the contents of the ramdisk

![Screenshot from 2023-05-29 09-05-00](https://github.com/MikhStas/Portals/assets/61974713/07a35ee1-d580-4cd6-a636-f4854ac667f7)
