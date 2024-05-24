import tkinter as tk
from tkinter import messagebox
import subprocess
from tkinter import simpledialog


class MainWindow:
    def __init__(self, master, client_socket):
        self.master = master
        self.master.title("Main Window")

        # 在这里使用传递过来的客户端套接字对象
        self.client_socket = client_socket

        self.label = tk.Label(self.master, text="Welcome to the Main Window")
        self.label.pack(padx=20, pady=20)

        self.balance_button = tk.Button(self.master, text="查询余额", command=self.check_balance)
        self.balance_button.pack(pady=10)

        self.withdraw_button = tk.Button(self.master, text="取款", command=self.withdraw_money)
        self.withdraw_button.pack(pady=10)

        self.quit_button = tk.Button(self.master, text="退出", command=self.exit_program)
        self.quit_button.pack(pady=10)

    def check_balance(self):
        # 向服务器发送查询余额的请求
        self.client_socket.sendall("BALA".encode())
        # 从服务器接收余额信息
        balance = self.client_socket.recv(1024).decode()
        balance = balance[5:]
        messagebox.showinfo("查询余额", f"您的余额为: {balance}")

    def withdraw_money(self):
        amount = simpledialog.askinteger("取款", "请输入取款金额:")
        if amount is not None:
            # 向服务器发送取款请求
            self.client_socket.sendall(f"WDRA {amount}".encode())
            # 从服务器接收取款结果
            result = self.client_socket.recv(1024).decode()
            if result == "525 OK!" or result == "525 OK":
                messagebox.showinfo("取款结果", f"取款成功: ${amount}")
            elif result == "401 ERROR!" or result == "401 ERROR":
                messagebox.showinfo("取款结果", "余额不足，取款失败")

    def exit_program(self):
        # 向服务器发送退出信号
        self.client_socket.sendall("BYE".encode())
        get_bye = self.client_socket.recv(1024).decode()
        if get_bye == "BYE":
            # 关闭socket连接
            self.client_socket.close()
            self.master.destroy()
            messagebox.showinfo("再见", "已退卡！")
        else:
            messagebox.showinfo("error", "退卡失败！")



def main(client_socket):
    root = tk.Tk()
    app = MainWindow(root, client_socket)
    root.mainloop()


if __name__ == "__main__":
    main()
