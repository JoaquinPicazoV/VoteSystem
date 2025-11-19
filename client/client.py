import socket
import sys

PUERTO = 65432

# Prácticamente se maneja toda la conexión y comunicación del cliente al servidor
def iniciar_cliente():
    direccion_entrada = input("Ingresa la dirección IP del servidor: ")
    DIRECCION_HOST = direccion_entrada.strip()

    if not DIRECCION_HOST:
        print("No se ingresó una dirección de host válida.")
        return

    print(f"Intentando conectar a {DIRECCION_HOST}:{PUERTO}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((DIRECCION_HOST, PUERTO))
            
            datos_iniciales = s.recv(1024)
            if datos_iniciales:
                print("="*40)
                respuesta = datos_iniciales.decode('utf-8')
                print(respuesta)
                print("="*40)
            else:
                print("Conexión inicial fallida. El servidor puede estar cerrado.")
                return
            
            if "Ya has votado" in respuesta:
                return

            while True:
                comando = input("Tu voto > ")
                
                if not comando:
                    continue
                
                s.sendall(comando.encode('utf-8'))
                
                if comando.strip().upper() == "EXIT":
                    break
                
                datos = s.recv(1024)
                if datos:
                    respuesta = datos.decode('utf-8')
                    print(f"Respuesta del Servidor: {respuesta}")
                    
                    if "Voto registrado exitosamente" in respuesta:
                        print("\nEl voto único fue emitido. Desconectando...")
                        break
                else:
                    print("El servidor cerró la conexión.")
                    break

        except ConnectionRefusedError:
            print(f"No se pudo conectar al servidor en {DIRECCION_HOST}:{PUERTO}. Asegúrate de que el servidor esté en ejecución.")
        except socket.gaierror:
            print(f"La dirección de host '{DIRECCION_HOST}' no es válida o no se pudo resolver.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")

    print("Cliente cerrado.")

if __name__ == "__main__":
    iniciar_cliente()