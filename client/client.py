import socket
import sys
import uuid 

PUERTO_DEFECTO = 65432

def iniciar_cliente():    
    direccion_entrada = input("Ingresa la dirección IP del servidor (ej: 192.168.x.x): ")
    entrada_limpia = direccion_entrada.strip()

    if not entrada_limpia:
        print("No se ingresó una dirección válida.")
        return

    if ':' in entrada_limpia:
        try:
            DIRECCION_HOST, puerto_str = entrada_limpia.rsplit(':', 1)
            PUERTO = int(puerto_str)
        except ValueError:
            print(f"Error: El puerto no es válido.")
            return
    else:
        DIRECCION_HOST = entrada_limpia
        PUERTO = PUERTO_DEFECTO

    print(f"Intentando conectar a {DIRECCION_HOST}:{PUERTO}...")


    MI_UUID = str(uuid.uuid4())
    print(f"Tu ID de votante generado es: {MI_UUID}")


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((DIRECCION_HOST, PUERTO))
            

            s.sendall(MI_UUID.encode('utf-8'))

            
            datos_iniciales = s.recv(1024)
            if datos_iniciales:
                print("="*40)
                respuesta = datos_iniciales.decode('utf-8')
                print(respuesta)
                print("="*40)
            else:
                print("Conexión inicial fallida.")
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

        except Exception as e:
            print(f"No se pudo conectar o hubo un error: {e}")

    print("Cliente cerrado.")

if __name__ == "__main__":
    iniciar_cliente()