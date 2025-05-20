import socket
import threading
import time
from gps_module import GPSModule
from motor_control import MotorControl
from servo_control import ServoControl

class ShipController:
    def __init__(self):
        self.gps = GPSModule()
        self.motor = MotorControl()
        self.servo = ServoControl()
        self.server_socket = None
        self.running = False
        self.gps_update_interval = 1  # GPS数据更新间隔(秒)

    def start_server(self, host='0.0.0.0', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.running = True
        
        print(f"Server started on {host}:{port}")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Connected to {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.start()
            except Exception as e:
                print(f"Error: {e}")
                break

    def handle_client(self, client_socket):
        try:
            # 验证是否为WebSocket连接请求
            data = client_socket.recv(1024).decode()
            print(data)
            
            if "Upgrade: websocket" in data:
                # 响应WebSocket握手请求
                self._handle_websocket_handshake(client_socket, data)
            
            # 创建并启动GPS发送线程
            gps_thread = threading.Thread(
                target=self.send_gps_periodically,
                args=(client_socket,)
            )
            gps_thread.daemon = True
            gps_thread.start()
            
            # 处理控制命令
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        print("Client disconnected")
                        break
                    
                    # 处理接收到的数据
                    message = data.decode(errors='ignore')
                    self.process_command(message)
                    
                except socket.error as e:
                    print(f"Socket error while receiving: {e}")
                    break
                
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            # 确保客户端套接字被关闭
            print("Closing client socket")
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass  # 忽略已关闭的套接字错误
            client_socket.close()

    def _handle_websocket_handshake(self, client_socket, request):
        """处理WebSocket握手请求"""
        import base64
        import hashlib
        
        # 提取Sec-WebSocket-Key
        key = None
        for line in request.split('\r\n'):
            if line.startswith('Sec-WebSocket-Key:'):
                key = line.split(':')[1].strip()
                break
                
        if key:
            # 计算WebSocket接受密钥
            magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
            accept_key = base64.b64encode(
                hashlib.sha1((key + magic_string).encode()).digest()
            ).decode()
            
            # 构建WebSocket握手响应
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n"
                "\r\n"
            )
            
            # 发送握手响应
            client_socket.send(response.encode())
            print("WebSocket handshake completed")

    def send_gps_periodically(self, client_socket):
        """定期发送GPS数据的线程函数"""
        try:
            while self.running:
                # 检查套接字是否已关闭
                if client_socket._closed:
                    print("Socket is closed, exiting GPS thread")
                    break
                    
                try:
                    gps_data = self.gps.get_current_position()
                    print(f"Sending GPS: {gps_data}")
                    
                    # 对于WebSocket连接，需要进行帧封装
                    if self._is_websocket(client_socket):
                        gps_data = self._encode_websocket_frame(gps_data)
                    
                    client_socket.send(gps_data.encode() if isinstance(gps_data, str) else gps_data)
                    time.sleep(self.gps_update_interval)
                    
                except socket.error as e:
                    print(f"Socket error while sending GPS: {e}")
                    break
                    
        except Exception as e:
            print(f"GPS thread error: {e}")

    def _is_websocket(self, client_socket):
        """检查是否为WebSocket连接"""
        # 简单实现：假设处理过握手的就是WebSocket连接
        return hasattr(client_socket, '_is_websocket') and client_socket._is_websocket
    
    def _encode_websocket_frame(self, message):
        """将消息编码为WebSocket帧"""
        # 简化的WebSocket帧编码，仅处理文本消息
        message_bytes = message.encode('utf-8')
        frame = bytearray()
        
        # 构建帧头部
        frame.append(0x81)  # FIN=1(最后一帧), OPCODE=1(文本帧)
        
        # 构建负载长度
        length = len(message_bytes)
        if length <= 125:
            frame.append(length)
        elif length <= 65535:
            frame.append(126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(127)
            frame.extend(length.to_bytes(8, 'big'))
            
        # 添加消息内容
        frame.extend(message_bytes)
        return bytes(frame)

    def process_command(self, command):
        # TODO: 实现命令处理逻辑
        pass

    def cleanup(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.motor.cleanup()
        self.servo.cleanup()

if __name__ == "__main__":
    controller = ShipController()
    try:
        controller.start_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        controller.cleanup()