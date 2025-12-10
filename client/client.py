import socket
import sys

PUERTO_DEFECTO = 65432

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        print("enviado: "+ip_local)
        return ip_local
    except Exception:
        return "127.0.0.1"

def iniciar_cliente():    
    direccion_entrada = input("Ingresa la dirección IP del servidor (ej: 192.168.1.10): ")
    entrada_limpia = direccion_entrada.strip()

    if not entrada_limpia:
        print("Debes ingresar una IP.")
        return

    DIRECCION_HOST = entrada_limpia
    PUERTO = PUERTO_DEFECTO
    
    if ':' in entrada_limpia:
        try:
            DIRECCION_HOST, puerto_str = entrada_limpia.rsplit(':', 1)
            PUERTO = int(puerto_str)
        except ValueError:
            print("Puerto inválido.")
            return

    mi_ip_local = obtener_ip_local()
    print(f"Detectado: Tu IP en la red es {mi_ip_local}")
    print(f"Conectando a {DIRECCION_HOST}:{PUERTO}...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((DIRECCION_HOST, PUERTO))
            
            s.sendall(f"CLIENT_IP:{mi_ip_local}".encode('utf-8'))
            
            datos_iniciales = s.recv(1024)
            mensaje_servidor = datos_iniciales.decode('utf-8')
            
            print("\n" + "="*40)
            print(mensaje_servidor)
            print("="*40)

            if "Ya has votado" in mensaje_servidor or "ERROR" in mensaje_servidor:
                return

            while True:
                comando = input("\nEscribe tu voto (ej: VOTE Juan.py) o EXIT > ")
                if not comando: continue
                
                s.sendall(comando.encode('utf-8'))
                
                if comando.strip().upper() == "EXIT":
                    break
                
                respuesta_voto = s.recv(1024).decode('utf-8')
                print(f"Servidor: {respuesta_voto}")
                
                if "Voto registrado" in respuesta_voto:
                    print("\n[DESCONECTANDO] Gracias por tu participación.")
                    break 

    except ConnectionRefusedError:
        print("No se pudo conectar. ¿El servidor está encendido?")
    except ConnectionResetError:
        print("El servidor cerró la conexión.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    iniciar_cliente()