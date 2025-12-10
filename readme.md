# 🗳️ Trabajo 3: Vote System

## 👥 Estudiantes
Sebastián Leiva - Joaquín Picazo

## ✨ Resumen del proyecto
Este proyecto implementa el **Caso 5: Vote System** para el Trabajo 3. El objetivo es crear un sistema de votación en donde los clientes pueden realizar votaciones eligiendo una opción con el comando **"VOTE [OPCIÓN]"**, para lo cual el servidor debe mostar en pantalla que se emitió un nuevo voto, el resumen del conteo y evitar que el mismo cliente (IP) vote más de una vez. Esto se debe llevar a cabo dockerizando el cliente y servidor y desplegarlo con Kubernetes (k8s).

## 📢 Recomendaciones previas
1) Contar con Python instalado, preferentemente la versión más estable y reciente
2) Contar con Docker y Kubernetes instalado (minikube, kubectl, etc.)

## 🛠️ Tecnologías utilizadas
1) 🐍 Python (Cliente-Servidor)
2) 🐳 Docker (Contenedores)
3) ☸️ Kubernetes (Orquestación)

# 💻 Ejecución y uso sin Docker ni Kubernetes (solo los archivos en python)
## 📂 Paso 1: Clonar repositorio
```bash
git clone {URL_repositorio_git}
```
## 🌐 Paso 2: Obtener IP de la máquina host (servidor)
```bash
hostname -I #En caso de linux (más recomendable usar linux)

ipconfig #En caso de windows
```
## 🖥️ Paso 3: Correr el servidor
Entrar al directorio del archivo python server.py
```bash
python3 server.py #En caso de linux (más recomendable usar linux)

python server.py #En caso de windows
```
## 📱 Paso 4: Conectarse con un dispositivo cliente
Entrar al directorio del archivo python client.py
```bash
python3 client.py #En caso de linux (más recomendable usar linux)

python client.py #En caso de windows
```
## 🔑 Paso 5: Ingresar la IP del servidor 
Al ejecutar el código en python del cliente, se solicitará la IP del servidor que hostea el sistema de votación. Usar la IP obtenida del paso 2.
## ✅ Paso 6: Efectuar votación
Seguir las instrucciones que vaya otorgando el sistema y realizar la votación. Solo se permite 1 votación por IP.

# 🐳☸️ Ejecución con Docker y Kubernetes
## 🐳 Dockerizar cliente y servidor + push a Docker Hub (Incluyendo el uso de imágenes puras de Docker Hub)
Ingresar a la raiz del proyecto y ejecutar en este orden:
```bash
docker build -t votesys-server:latest -f server/Dockerfile ./server
docker build --no-cache -t joaquinpicazo/votesys_client:client-latest -f client/Dockerfile ./client

docker tag votesys-server:latest joaquinpicazo/votesys_server:server-latest
docker tag votesys-client:latest joaquinpicazo/client:client-latest

# Se necesita iniciar sesión en Docker Hub para hacer efectivo el push
docker push joaquinpicazo/votesys_server:server-latest
docker push joaquinpicazo/votesys_client:client-latest

# EJECUCIONES USANDO LAS IMAGENES DOCKER
docker run --name votesys-server-instance -p 65432:65432 joaquinpicazo/votesys_server:server-latest #PARA EJECUTAR LA IMAGEN DEL SERVIDOR DE DOCKER HUB
docker run -it --rm joaquinpicazo/votesys_client:client-latest #PARA EJECUTAR LA IMAGEN DEL CLIENTE DE DOCKER HUB
```
Al ejecutar el cliente, conectarse colocando la IP asignada a la máquina que hostea el servidor.
```bash
hostname -I #Ejecutar este comando el la maquina que hostea el server para saber su IP en la red LAN
```

OBS: Si ya hay una instancia con ese nombre y hay problema para ejecutar el servidor, basta con ejecutar los siguientes comandos y volver a ejecutar el servidor con la imagen de Docker Hub
```bash
docker stop votesys-server-instance

docker rm votesys-server-instance
```

# ☸️ Utilizar kubernetes para ofrecer el servidor de votación
⚙️ Es importante inicializar minikube con:
```bash
minikube start --driver=docker
```
🚀 Paso 1: Ingresar al directorio /kubernetes del proyecto y ejecutar los yaml. Luego esperar unos minutos.
```bash
kubectl aplly -f server-deploy.yaml

kubectl apply -f server-service.yaml

kubectl aplly -f client-deploy.yaml
```
🗺️ Paso 2: Obtener la IP que tiene asignada la computadora host en la red LAN y el nombre del pods.
```bash
hostname -I # IP en la red local
kubectl get pods -l component=server # nombre del pods en columna NAME
```
🔗 Paso 3: Realizar un port forward de la computadora a nuestro servicio de kubernetes (dejar corriendo en otra pestaña de la terminal)
```bash
kubectl port-forward {nombre_del_pods} 65432:65432 --address {ip_asignada_red_LAN}
```
📝 Paso 4: Revisar los logs del servicio para ver interacciones de los clientes (dejar corriendo en otra pestaña de la terminal)
```bash
kubectl logs -f {nombre_del_pods} #Nombre del pod se obtiene en el paso 2
```
💻 Paso 5: Conectar un cliente al servicio existente en Kubernetes usando la imagen de cliente de Docker Hub
```bash
docker run -it --rm --network host --hostname "{tu_usuario}" joaquinpicazo/votesys_client:client-latest #Cuando pida ip:puerto ingresar la IP obtenida en el paso 2 y puerto 65432
```