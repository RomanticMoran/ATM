import socket
import time
import logging
import sys
import threading
import mysql.connector

# 连接数据库
def connect_to_mysql(host, username, password, database):
    try:
        # 创建连接
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        print("成功连接到MySQL数据库！")
        return connection
    except mysql.connector.Error as error:
        print("连接到MySQL数据库失败：", error)
        return None

# 示例连接到本地MySQL服务器
connection = connect_to_mysql(
    host="localhost",
    username="root",
    password="123456",
    database="network"
)

# 在这里可以执行你的数据库操作
# # 关闭连接
# if connection:
#     connection.close()
#     print("数据库连接已关闭。")

def check_username(connection, account):
    cursor = connection.cursor()
    query = "SELECT * FROM user WHERE user_id = %s"
    cursor.execute(query, (account,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return 1
    else:
        return 0


def validate_password(connection, username, password):
    cursor = connection.cursor()
    query = "SELECT user_password FROM user WHERE user_id = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        db_password = result[0]
        if password == db_password:
            return 1
    return 0


def get_amount(connection, username, password):
    cursor = connection.cursor()
    query = "SELECT user_password, amount FROM user WHERE user_id = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        db_password = result[0]
        db_amount = result[1]
        if password == db_password:
            return db_amount
    return 0



def withdraw_amount(connection, username, password, amount):
    cursor = connection.cursor()
    query = "SELECT user_password, amount FROM user WHERE user_id = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        db_password = result[0]
        if password == db_password:
            update_query = "UPDATE user SET amount = amount - %s WHERE user_id = %s"
            amount_to_add = amount
            account_to_update = username
            cursor.execute(update_query, (amount_to_add, account_to_update))
            connection.commit()
    cursor.close()
    return 0



#日志文件
format = "%(asctime)s - %(levelname)s - %(message)s"

date_FORMAT = "%m/%d/%Y %H:%M:%S %p"

file_handler = logging.FileHandler('timelog.log')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    format=format,
    datefmt=date_FORMAT,
    level=logging.DEBUG,
    handlers=[
        file_handler,
        stream_handler
    ]
)


def handle_client(client_socket):
    while True:
        # 接收客户端发送的数据
        data_1 = client_socket.recv(1024).decode()
        if not data_1:
            logging.warning("No data!")
            break

        operation_1, account = data_1.split(' ')


        if operation_1 == "HELO" and check_username(connection, account) == 1:
            client_socket.sendall("500 AUTH REQUIRE".encode())
        else:
            client_socket.sendall("401 ERROR!".encode())  # 发送验证失败的消息

        # 解析客户端发送的账号和密码

        data_2 = client_socket.recv(1024).decode()
        operation_2, password = data_2.split(' ')

        # 验证账号和密码是否匹配
        if operation_2 == "PASS" and validate_password(connection, account, password) == 1:
            client_socket.sendall("525 OK!".encode())  # 发送验证通过的消息
            logging.debug(f"User {account} login successful.")
            while True:
                # 接收客户端的操作请求
                data_3 = client_socket.recv(1024).decode()

                if data_3 == "BALA":
                    logging.debug(f"User {account} balance query signal has been received.")
                    # 查询余额
                    balance = str(get_amount(connection, account, password))
                    client_socket.sendall(f"AMNT {balance}".encode())
                elif data_3 == "BYE":
                    client_socket.sendall("BYE".encode())
                    break  # 退出
                elif data_3[:4] == "WDRA":
                    operation_3, amountstr = data_3.split(' ')
                    logging.debug(f"User {account} balance withdrawal signal has been received.")
                    # 取款操作
                    amount = int(amountstr)
                    if amount <= get_amount(connection, account, password):
                        withdraw_amount(connection, account, password, amount)
                        client_socket.sendall("525 OK!".encode())  # 取款成功
                        logging.debug(f"User {account} withdraws {amountstr} yuan.")
                    else:
                        client_socket.sendall("401 ERROR!".encode())  # 余额不足，取款失败
                        logging.error(f"Insufficient balance, user {account} fails to withdraw money!")

                else:
                    client_socket.sendall("401 ERROR!".encode())  # 无效操作
                    logging.error(f"Invalid user {account} operation!")
        else:
            client_socket.sendall("401 ERROR!".encode())  # 发送验证失败的消息

    client_socket.close()

def main():
    server_ip = '0.0.0.0'  # 服务器IP地址
    server_port = 2525

    # 创建TCP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定IP地址和端口号
    server_socket.bind((server_ip, server_port))

    # 设置最大连接数
    server_socket.listen(5)

    print("等待客户端连接...", time.asctime(time.localtime(time.time())))

    while True:
        # 等待客户端连接请求
        client_socket, client_address = server_socket.accept()
        print(f"客户端 {client_address} 连接成功！", time.asctime(time.localtime(time.time())))

        # 处理客户端请求
        th = threading.Thread(target=handle_client, args=(client_socket,))
        th.start()
        # handle_client(client_socket)

if __name__ == "__main__":
    main()
