import os
import base64
import shutil
import zipfile
import time
import tkinter.filedialog
import re
import random
from tkinter import *
from tkinterdnd2 import *
from ttkbootstrap import *
from ttkbootstrap.constants import *
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from tkinter import messagebox


# 这版 文件加密解密分块儿多组
class FileAES:

    def __init__(self):
        self.keys = ''  # 将密钥转换为字符型数据，16、24或32位
        self.mode = AES.MODE_ECB  # 操作模式选择ECB
        self.unicode = 'utf-8'  # 默认字符集
        self.compressPostfix = '.skj'
        self.version = "V1.1"
        self.ui()

    def ui(self):
        theme = ['vapor', 'solar', 'pulse', 'minty']
        # style = Style(theme=theme[0])
        # win = style.master
        win = TkinterDnD.Tk()
        win.title("内部解压工具 " + self.version)
        win.resizable(width=False, height=False)
        # win.minsize(560, 545) # 最小尺寸
        # win.maxsize(560, 545) # 最大尺寸
        # sw = win.winfo_screenwidth()
        # sh = win.winfo_screenheight()
        # ww = 350
        # wh = 200
        # x = (sw - ww) / 2
        # y = (sh - wh) / 2
        # win.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        # win.resizable(0, 0)
        self.file_names = []
        self.encrypt_string = StringVar()  # 加密字符串
        self.encrypt_string.set("")  # 设置加密字符串初始值
        self.folder_name = StringVar()
        self.folder_name.set("")
        self.encrypt_name = Label(win, text="密码: ")
        self.text = Text(win,
                         width=35,
                         height=5,
                         undo=True,
                         autoseparators=False)
        self.text.configure(state='disabled')
        self.pack_name = Label(win, text="压缩包名：")
        self.pack_name_value = Entry(win, textvariable=self.folder_name)
        self.encrypt_string_value = Entry(win,
                                          textvariable=self.encrypt_string)
        self.btn = Button(win, text="选择文件", command=self.select_file, width=12)
        self.btn1 = Button(win,
                           text="执行",
                           width=19,
                           command=self.handler_file,
                           style=(INFO, OUTLINE))

        self.text.grid(row=0, column=0, columnspan=4, rowspan=4)  # 显示文字区域
        # self.pack_name.grid(row=5, column=0, sticky="")  # 压缩 tip
        # self.pack_name_value.grid(row=5, column=1, sticky="")  # 压缩 input
        self.encrypt_name.grid(row=6, column=0, sticky="")  # 加密 tip
        self.encrypt_string_value.grid(row=6, column=1, sticky="")  # 加密 input
        self.btn.grid(row=7, column=0, sticky="")  # 按钮选择文件
        self.btn1.grid(row=7, column=1, sticky="")  # 执行··
        win.drop_target_register(DND_FILES)
        win.dnd_bind('<<Drop>>', self.get_path)
        win.mainloop()

    def get_path(self, event):
        self.file_names.clear()  # 清空列表
        self.file_names += event.data.split(" ")
        self.text.configure(state='normal')  # 打开锁
        self.text.delete('1.0', END)
        string_filename = ""
        for i in range(0, len(self.file_names)):
            self.file_names[i] = re.sub(r'{|}', '', self.file_names[i])
            string_filename += self.file_names[i] + "\n"
        self.text.insert(INSERT, "您选择的文件是：\n" + string_filename)
        self.text.configure(state='disabled')  # 上锁

    def add_to_16(self, text):
        if len(text.encode(self.unicode)) % 16:
            add = 16 - (len(text.encode(self.unicode)) % 16)
        else:
            add = 0
        text = text + ('\0' * add)
        return text.encode(self.unicode)

    # 加密函数
    def encrypt(self, text):
        key = self.keys.encode(self.unicode)
        mode = AES.MODE_ECB
        text = self.add_to_16(text)
        cryptos = AES.new(key, mode)

        cipher_text = cryptos.encrypt(text)
        return b2a_hex(cipher_text)

    # 解密函数
    def decrypt(self, text):
        key = self.keys.encode(self.unicode)
        mode = AES.MODE_ECB
        cryptor = AES.new(key, mode)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')

    # 函数功能是zip_file_list所有文件，和zip_dir_list所有目录下的所有文件，被压缩到一个zip_file_name的压缩文件中
    def my_zip_function(self,
                        zip_file_name,
                        zip_file_list=[],
                        zip_dir_list=[]):
        # 压缩文件最后需要close，为了方便我们直接用with
        with zipfile.ZipFile(zip_file_name, "w") as zip_obj:
            # 压缩文件
            for tmp_file in zip_file_list:
                with open(tmp_file, 'rb') as f:
                    streams = f.read()
                    zip_obj.writestr(os.path.split(tmp_file)[1], streams)
            # 压缩目录
            for tmp_dir in zip_dir_list:
                # zipfile没有直接压缩目录的功能，要压缩目录只能遍历目录一个一个文件压。
                for root, dirs, files in os.walk(tmp_dir):
                    # 如果想要目录为空时仍将该目录压缩进去，该目录也要压缩一遍；反之请将以下行注释掉
                    zip_obj.write(root)
                    for tmp_file in files:
                        # 拼接文件完整目录，不然只用文件名代码找不到文件
                        tmp_file_path = os.path.join(root + '/', tmp_file)
                        zip_obj.write(tmp_file_path)

    # 函数功能是遍历压缩文件中的所有文件
    def my_traversal_zip_function(self, zip_file_name):
        with zipfile.ZipFile(zip_file_name, "r") as zip_obj:
            all_file_list = zip_obj.infolist()

    # 函数的功能是将压缩文件直接解压
    def my_unzip_function(self, zip_file_name, path):
        with zipfile.ZipFile(os.path.join(path + '/', zip_file_name),
                             "r") as zip_obj:
            zip_obj.extractall(
                os.path.join(path + '/',
                             os.path.splitext(zip_file_name)[0]))

    # 选取文件
    def select_file(self):
        self.file_names.clear()  # 清空列表
        self.file_names += list(
            tkinter.filedialog.askopenfilenames(title="选取要操作的文件"))
        if len(self.file_names) != 0:
            self.text.configure(state='normal')  # 打开锁
            self.text.delete('1.0', END)
            string_filename = ""
            for i in range(0, len(self.file_names)):
                string_filename += str(self.file_names[i]) + "\n"
            self.text.insert(INSERT, "您选择的文件是：\n" + string_filename)
            self.text.configure(state='disabled')  # 上锁
        else:
            self.text.insert(INSERT, "您没有选择任何文件")

    # 计算时间差是否大于一天，返回布尔值
    def diffTimeGreaterThanOne(formerly):
        today = int(str(time.time()).split('.')[0])
        day = (today - formerly) / (24 * 3600 * 1000)
        boolean = 1 if day > 1 else 0
        return boolean

    # 解密文件
    def deciphering_file(self, file_list, dirs):
        name = re.sub(r'.skj\d+$', '', file_list[0])
        datas = ""
        for i in file_list:
            nameNow = re.sub(r'.skj\d+$', '', i)
            if name != nameNow:
                stream = self.decrypt(datas.encode('ascii'))
                data = base64.b64decode(stream)
                with open(os.path.join(dirs + '/', name), "wb") as new_file:
                    new_file.write(data)
                name = nameNow
                datas = ""
            with open(os.path.join(dirs + '/', i), "rb") as f:
                datas += f.read().decode('ascii')
            os.remove(os.path.join(dirs + '/', i))  # 删除中间文件
        stream = self.decrypt(datas.encode('ascii'))  # 把解密后的内容存入stream，准备写入文件
        data = base64.b64decode(stream)  # 对二进制文件转码
        with open(os.path.join(dirs + '/', name), "wb") as new_file:
            new_file.write(data)
            name = nameNow

    # 解密文件夹
    def deciphering_folder(self, dirs_file_path, dirs_file_name, dirs):
        with open(dirs_file_path, "rb") as f:
            stream = self.decrypt(f.read())
            data = base64.b64decode(stream)
            name = os.path.splitext(dirs_file_name)[0]
            with open(os.path.join(dirs + '/', name), "wb") as new_file:
                new_file.write(data)

    # 加密文件
    def encrypt_file(self, file_path):
        all_file = []
        num = random.randint(3, 6)
        with open(file_path, "rb") as f:
            stream = base64.b64encode(f.read())
            data = self.encrypt(stream.decode(self.unicode))  # 对 2 进制内容进行加密
            dataArr = self.slice_arr(data, num)
            index = 1
            for datas in dataArr:
                file_name = file_path + self.compressPostfix + str(index)
                all_file.append(file_name)
                with open(file_name, "wb") as new_file:
                    new_file.write(datas)  # 将加密后的内容写入文件内
                index += 1
        return all_file

    # 分割数组
    def slice_arr(self, datas, num):
        arr = []
        length = len(datas)
        if length == 0:
            return arr
        t = math.ceil(length / num)
        start = 0
        end = 0
        i = 0
        while 1:
            end = start + t
            remainder = length - t * (i - 1)  # 剩余
            if remainder < t:
                break
            data = datas[start:end] if remainder >= t else datas[end:length]
            if (len(data) > 0):
                arr.append(data)
            start = end
            i += 1
        return arr

    # 加密或解密多个文件（方式：先将对应文件分别加密，再将加密后的文件压缩进一个压缩包）
    # 对于一个文件分成多个文件加密的实现方式：1. 先将文件进行加密 2. 将加密后的密文分成数份，分别放入不同的文件 3. 将文件统一进行打包
    def handler_file(self):
        # 把密码进行补全，得到16、24或32位
        str = self.encrypt_string.get()
        length = len(str)
        if length == 0:
            messagebox.showinfo('提示', '请输入压缩密码')
            return 0
        # 超出32位自动截取前32位
        self.keys = str.rjust(
            16, '1') if length > 0 and length < 16 else str.rjust(
                24, '1') if length > 16 and length < 24 else str.rjust(
                    32, '1') if length > 24 and length < 32 else str[0:32]
        if len(self.file_names) > 0:
            # 判断压缩名称是否为空，为空制时间戳为包名
            if self.folder_name.get() == '':
                self.folder_name.set(time.strftime("%Y.%m.%d-%H-%M-%S"))
            else:
                self.folder_name.set(self.folder_name.get().replace(' ', ''))
            self.zip_file_name = self.folder_name.get() + ".zip"
            self.zip_file_list = []
            self.zip_dir_list = []
            handler_type = ''
            for file_path in self.file_names:
                folder = []
                path = os.path.split(file_path)[0]  # 路径
                self.zip_path = path  # 更新压缩包路径
                name = os.path.split(file_path)[1]  # 文件名
                if os.path.splitext(file_path)[1] == '.zip':
                    handler_type = 'unpack'
                    dirs = os.path.join(path + '/', os.path.splitext(name)[0])
                    folder_exist_flag = 1
                    if not os.path.exists(dirs):
                        # 文件夹不存在
                        os.mkdir(dirs)
                        folder_exist_flag = 0
                        # os.makedirs(dirs)
                    self.my_unzip_function(name, path)
                    # if os.path.isfile(os.path.join(dirs + '/', name)):
                    # os.remove(os.path.join(dirs + '/', name))  # 默认剔除已存在的源文件
                    file_list = os.listdir(dirs)
                    file_list.sort()  # 对数据进行排序 正序
                    for index in range(len(file_list)):
                        # 对文件夹下的原始文件过滤，不计入分片文件
                        if os.path.splitext(
                                re.sub(r'.skj\d+$', '.skj', file_list[index])
                        )[1] != self.compressPostfix:
                            del file_list[index]
                            break
                            # index -= 1
                    # for dirs_file_name in file_list:
                    #     dirs_file_path = os.path.join(dirs, dirs_file_name)
                    #     self.deciphering_folder(dirs_file_path, dirs_file_name,
                    #                             dirs)
                    try:
                        self.deciphering_file(file_list, dirs)
                    except:
                        if folder_exist_flag == 0:
                            shutil.rmtree(dirs)
                        messagebox.showerror('提示', '密码错误')
                        break
                    messagebox.showinfo('提示', '解压完成')
                # elif os.path.splitext(file_path)[1] == self.compressPostfix:
                #     handler_type = 'deciphering'  # 解密
                #     self.deciphering(file_path)
                # else:
                #     handler_type = 'pack'
                #     all_file = self.encrypt_file(file_path)
                #     # folder.append(os.path.split(file_path)[1] + self.compressPostfix)
                #     folder += all_file
                #     self.zip_file_list += folder
                #     self.zip_dir_list = []
                # if handler_type == 'pack':
                #     self.my_zip_function(
                #         os.path.join(self.zip_path, self.zip_file_name),
                #         self.zip_file_list, self.zip_dir_list)
                # # self.my_traversal_zip_function(self.zip_file_name)
                # folders = os.path.join(self.zip_path,
                #                        os.path.splitext(self.zip_file_name)[0])
                # if not os.path.isdir(folders):
                #     os.makedirs(folders)
                #     for i in self.zip_file_list:
                #         shutil.move(i, folders)
                #         # os.remove(i)  # 删除加密后的中间文件
                #         messagebox.showinfo('提示', '压缩完成')
        else:
            self.text.configure(state='normal')  # 打开锁
            self.text.delete('1.0', END)
            self.text.insert(INSERT, "您没有选择任何文件")
            self.text.configure(state='disabled')  # 上锁
        self.encrypt_string.set("")


if __name__ == '__main__':
    # decode() 转字符串 encode() 转字节流
    FileAES()
