import socket
import tkinter as tk
from tkinter import messagebox
import subprocess
from main import MainWindow  # 导入主界面类


class LoginWindow:
    def __init__(self, master, client_socket):
        self.master = master
        self.master.title("登录")

        # 创建账号输入框
        self.username_label = tk.Label(self.master, text="账号:")
        self.username_label.grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        # 创建密码输入框
        self.password_label = tk.Label(self.master, text="密码:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(self.master, show="*")  # 使用 show="*" 来隐藏密码
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        # 创建登录按钮
        self.login_button = tk.Button(self.master, text="登录", command=self.login)
        self.login_button.grid(row=2, columnspan=2, padx=10, pady=5)


        # 在这里接收传递过来的客户端套接字对象
        self.client_socket = client_socket

    def login(self):
        account = self.username_entry.get()
        password = self.password_entry.get()

        # 向服务器发送账号和密码
        account_info1 = f"HELO {account}"
        self.client_socket.sendall(account_info1.encode())
        modifiedSentence = self.client_socket.recv(1024)
        response = modifiedSentence.decode()  # 接收是否存在账户信息：返回的str类型

        if response == '500 AUTH REQUIRE' or response == '500 AUTH REQUIRED!' or response == '500 AUTH REQUIRE!':
            account_info2 = f"PASS {password}"
            self.client_socket.sendall(account_info2.encode())
            # 接收服务器的响应
            modifiedSentence = self.client_socket.recv(1024)
            response = modifiedSentence.decode()  # 接收是否存在账户信息：返回的str类型
        else:
            print("没有该账号")

        if response == '525 OK' or response == '525 OK!':
            # print("ok")
            # 创建主界面并传递客户端套接字对象
            root = tk.Tk()
            main_window = MainWindow(root, self.client_socket)
            root.mainloop()
        elif response == "401 ERROR!" or response == "401 ERROR":
            messagebox.showerror("Server Response", "密码错误！")

        # 关闭客户端套接字（这里不需要关闭，因为在主界面中关闭）
        # self.client_socket.close()


def main():
    root = tk.Tk()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_ip = input('请输入ip')
    if connect_ip == '0':
        connect_ip = '192.168.43.108'
    client_socket.connect((connect_ip, 2525))  # 连接服务器
    app = LoginWindow(root, client_socket)
    root.mainloop()


if __name__ == "__main__":
    main()
