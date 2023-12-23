
import os
import sys
import colorama
from colorama import Fore

from socket import *
        
PORT = 8668
FILE_ROOT = "D:\\我的文档\\学习\\ESP32\\update\\"
SEND_FILE_DICT = {"下位机程序.py": "main.py"}

SAVE_PATH = "D:\\我的文档\\学习\\ESP32\\download\\"
DOWNLOAD_LIST = ['log.txt', 'main.py']

esp32 = None # global

SUCCESS = 0
NOTICE = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

"""
@ Brief:    Esp remote control main module
"""

class ESP32Ctrl(object):
    def __init__(self, port):
        self.port = port
        
        self.address = ('', self.port)
        self.usock = socket(AF_INET, SOCK_DGRAM)
        self.usock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.usock.bind(self.address)
        
        self.tsock = None
    
    def connect(self):
        while True:
            print('waiting recv...')
            data, self.address = self.usock.recvfrom(1024)
            data = data.decode()

            if data == "[HI]":
                break
            
        self.ipaddr = self.address[0]
        
        self.tsock = socket(AF_INET, SOCK_STREAM)

        server_ip, server_port = self.ipaddr, self.port
        self.tsock.connect((server_ip, server_port))

        self.tsock.settimeout(5)
        
        print(f"TCP connected to ESP32 {self.ipaddr}.")
    
    def isconnected(self):
        return self.tsock != None
    
    def recv_signal(self, description_of_this_time, expected_dat = None):
        try:
            dat = self.tsock.recv(1024).decode()
            if len(dat) == 0:
                print(f"ERROR: Lost Connection when {description_of_this_time}!")
                self.tsock = None
                return "", CRITICAL
            
            if expected_dat != None and dat != expected_dat:
                print(f"ERROR: Response Invalid when {description_of_this_time} : {dat}")
                return dat, ERROR
            
            return dat, SUCCESS
            
        except Exception as exc:
            print(f"ERROR: No Response when {description_of_this_time}. ({exc})")
            return "", WARNING

    def send_signal(self, dat):
        try:
            self.tsock.send(dat.encode())
            return True
        except:
            print(f"Send signal failed. {dat}")
            return False
        
    def update(self, root_path, file_name_dict):
        self.send_signal("[UPDATE]")
        dat, ret = self.recv_signal("start of update", "[READY]")
        if ret >= WARNING:
            return ret

        for file_name in file_name_dict:
            
            # send file name and wait for response
            send_dat = "[{file_name}]".format(file_name = file_name_dict[file_name])
            self.tsock.send(send_dat.encode())
            dat, ret = self.recv_signal(f'sending file_name {root_path + file_name}', '[NAME_COPIED]')
            if ret >= WARNING:
                return ret
            
            # send file content and wait for response
            content = ""
            with open(root_path + file_name, "r+") as f:
                arrLines = f.readlines()
                content = "".join(arrLines)
                # for line in arrLines:
                #     tsock.send(line.encode())
            
            content += "[EOF]"
            self.tsock.send(content.encode())
            
            dat, ret = self.recv_signal(f'sending file_content {root_path + file_name}', '[CONTENT_COPIED]')
            if ret >= WARNING:
                return ret
            
            print(f"Successfully send file {root_path + file_name}.")

        self.send_signal("[END_OF_UPDATE]")
        dat, ret = self.recv_signal("end of update.", "[FINISH]")
        if ret >= WARNING:
                return ret
            
        return SUCCESS
    
    def download(self, file_list, save_path):
        self.send_signal("[DOWNLOAD]")
        dat, ret = self.recv_signal("start of download", "[READY]")
        if ret >= WARNING:
                return ret
        
        if not save_path.endswith('\\'):
            save_path += '\\'
        
        for file_name in file_list:
            self.send_signal(f"[{file_name}]")
            with open(save_path + file_name, "w+") as f:
                while True:
                    dat, ret = self.recv_signal(f"recv file_content {file_name}")
                    if ret >= WARNING:
                        return ret
                    
                    if dat == "[INVALID_FILE_PATH]":
                        self.send_signal("[COPYTHAT]")
                        return NOTICE
                    
                    if dat.endswith('[EOF]'):
                        dat = dat[: -len('[EOF]')]
                        f.write(dat)
                        break
                    
                    f.write(dat)
            self.send_signal('[CONTENT_COPIED]')
            
            print(f"Successfully download file {file_name}")
        
        self.send_signal('[END_OF_DOWNLOAD]')
        dat, ret = self.recv_signal(f"end of download.", "[FINISH]")
        if ret >= WARNING:
            return ret
        return SUCCESS
    
    def get_file_list(self):
        self.send_signal("[GETFILELIST]")
        dat, ret = self.recv_signal("get file list")
        if ret >= WARNING:
            return dat, ret
            
        # print(f"GetFileList success: {dat}")
        return dat, SUCCESS
    
    def delete(self, file_name):
        self.send_signal("[DELETE]")
        dat, ret = self.recv_signal("start of delete", "[READY]")
        if ret >= WARNING:
               return ret
            
        self.send_signal(f"[{file_name}]")
        dat, ret = self.recv_signal("start of delete")
        if ret >= WARNING:
            return ret
        
        if dat == "[INVALID_FILE_PATH]":
            print("In Delete(), Invalid File Path.")
            return NOTICE
        
        if dat == '[FINISH]':
            print(f"Successfully delete file {file_name}")
            return SUCCESS
        
        print(f"Invalid Response when delete(). {dat}")
        return ERROR
    
    
    def reboot(self):
        self.send_signal('[REBOOT]')
        dat, ret = self.recv_signal('asking to reboot.', "[READY]")
        if ret >= WARNING:
            return ret
        
        return SUCCESS
    
    def close(self):
        try:
            self.usock.close()
            self.tsock.close()
            return SUCCESS
        except:
            return ERROR

esp32 = ESP32Ctrl(PORT)


"""
@ Brief:     A command line manager

"""
class COMMANDER(object):
    def __init__(self):
        colorama.init()

        self.cwd_dict = {}

    def cwdprint(self):
        cwd_this = os.getcwd().lower()
        print(Fore.YELLOW + f'ESPREMOTE {cwd_this}> ' + Fore.RESET, end = "")

    def update_cwd(self):
        cwd_this = os.getcwd()
        disk = cwd_this[0]
        self.cwd_dict.update({disk : cwd_this})

    def get_command(self):
        return self.inputcommand()
    
    def inputcommand(self):
        self.cwdprint()
        command = input().strip()
        return command
    
    def command_handler(self, command):
        arg_list = command.split(" ")
        op = arg_list [0].lower()

        if op in ['cd']:
            try:
                command = command[len(op + " ") : ].lower()
                command.strip("\"\'")
                
                for disk in 'cdefgh':
                    if command.startswith(disk + ':'):
                        os.chdir(command)
                        return
                
                os.chdir( './' + command)
                
                self.update_cwd()
            except Exception as exc:
                print(Fore.RED + f"ERROR: {exc}" + Fore.RESET)
            
            return
        
        elif op in ['c:', 'd:', 'e:', 'f:', 'g:', 'h:']:
            try:
                disk_tobe = op[0].upper()
                if disk_tobe in self.cwd_dict:
                    cwd_tobe = self.cwd_dict[disk_tobe]
                else:
                    cwd_tobe = op
                    self.cwd_dict.update({disk_tobe : cwd_tobe})
                os.chdir(cwd_tobe)
            except Exception as exc:
                print(Fore.RED + f"ERROR: {exc}" + Fore.RESET)

            return
        
        elif op in ['espremote']:
            help_info = {
"help" : """
Usage: espremote COMMAND [args] ...

Espremote is a tool to control esp32 boards over certain protocol.
Using espremote you can remotely connect to the board, manage file system
and even update or download files.

Command:
  conn    Connect to the board.
  ls      List contents of a directory on the board.
  mkdir   (Create a directory on the board. **UNDONE**)
  put     Put a file (or a folder and its content **UNDONE**) on the board.
  dnld    Download a file from the board.
  reset   Perform hard reset/reboot of the board.
  rm      Remove a file from the board.
  rmdir   (Forcefully remove a folder and all its children from the board. **UNDONE**)
  run     (Run a script and print its output. **UNDONE**)
""",
"put": """
Descrp: Put a file (or a folder and its content **UNDONE**) on the board.
Usage:  espremote put file_name [save_name]
""",
"dnld" : """
Descrp: Download a file from the board.
Usage:  espremote dnld file_path save_path
""",
"reset" : """
Descrp: Perform hard reset/reboot of the board.
Usage:  espremote reset
""",
"rm" : """
Descrp: Remove a file from the board.
Usage:  espremote rm file_path
""",
}
            if len(arg_list) == 1 or arg_list[1] == 'help':
                print(help_info['help'])
                return
                
            op2 = arg_list[1].lower()
            arg_list = arg_list[2:]
            # UNDONE please connect first
            
            if op2 in ['conn']:
                esp32.connect()
                return
            elif op2 in ['ls']:
                if not esp32.isconnected():
                    print(Fore.RED + f"INFO: Please connect to the board before ls." + Fore.RESET)
                    return
                
                file_list, _ = esp32.get_file_list()
                print(file_list)
                return
            
            elif op2 in ['mkdir']:
                print("This command is not completed.")
                return
            
            elif op2 in ['put']:
                if not esp32.isconnected():
                    print(Fore.RED + f"INFO: Please connect to the board before put." + Fore.RESET)
                    return
                
                # arg_str = " ".join(arg_list[2 :])
                # if arg_str.find('\"') >= 0 or arg_str.find('\'') >= 0:
                #     arg_str.replace("\"", "\'")
                #     arg_list2 = [argu.strip() for argu in arg_str.split("\'") if not argu.isspace()]
                
                # else:
                #     arg_list2 = arg_list[2 :]
                # arg_list = arg_list2
                
                if len(arg_list) == 0:
                    print(help_info["put"])
                    return
                
                file_path = arg_list[0].lower()
                if len(arg_list) == 1:
                    save_name = os.path.basename(file_path)
                else:
                    save_name = arg_list[1].lower()
                
                for disk in 'cdefgh':
                    if file_path.startswith(disk + ':'):
                        
                        esp32.update("", {file_path: save_name})
                        return
                    
                cwd_this = os.getcwd()
                file_path = os.path.join(cwd_this, file_path)
                dir_path = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                
                esp32.update(dir_path, {file_name: save_name})
                
                return
            
            elif op2 in ['dnld']:
                if not esp32.isconnected():
                    print(Fore.RED + f"INFO: Please connect to the board before dnld." + Fore.RESET)
                    return
                if len(arg_list) == 0:
                    print(help_info["dnld"])
                    return
                
                file_path = arg_list[0].lower()
                save_path = arg_list[1].lower()
                
                for disk in 'cdefgh':
                    if save_path.startswith(disk + ':'):
                        esp32.download([file_path], save_path)
                        return
                    
                save_path = os.path.join(os.getcwd(), save_path)
                esp32.download([file_path], save_path)
                
                return
            
            elif op2 in ['reset']:
                if not esp32.isconnected():
                    print(Fore.RED + f"INFO: Please connect to the board before reset." + Fore.RESET)
                    return
                
                esp32.reboot()
                return
            
            elif op2 in ['rm']:
                if not esp32.isconnected():
                    print(Fore.RED + f"INFO: Please connect to the board before rm." + Fore.RESET)
                    return
                
                if len(arg_list) == 0:
                    print(help_info["dnld"])
                    return
                file_path = arg_list[0].lower()
                esp32.delete(file_path)
                return

            elif op2 in ['rmdir']:
                print("This command is not completed.")
                return
            
            elif op2 in ['run']:
                print("This command is not completed.")
                return
            
            else:
                print(Fore.RED + f"ERROR: Invalid command \"{op2}\"." + Fore.RESET)
                print(help_info['help'])
                return
            
        else:
            print(Fore.RED + f"ERROR: Invalid operation \"{op}\"." + Fore.RESET)
            return
        
        
if __name__ == "__main__":
    
    cmd = COMMANDER()
    
    while True:
        command = cmd.inputcommand()
        cmd.command_handler(command)
        
