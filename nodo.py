
import redis
import py2p
import socket
import sys,os
import netifaces as ni
ip = ni.ifaddresses(sys.argv[1])[ni.AF_INET][0]['addr']

#CONEXIÓN A REDIS (TRACKER)
r = redis.Redis(host="10.1.2.203", port=6380)


#CONSTRUCTOR
class Node():

    def __init__(self,ip,port,recurso):

        self.socket = f"{ip}:{port}"
        self.recurso = recurso
        self.data = {}
        self.sock = None
        self.predecessor = None
        self.successor = None

    def join(self):
        
        self.sock = py2p.ChordSocket(self.socket.split(':')[0],int(self.socket.split(':')[1]))
        self.sock.join()

        lista = self.get_tracker_list()
        if lista:
            ip = [r.hget(self.recurso,x.decode("utf8")).decode("utf8") for x in lista][0]    
            self.sock.connect(ip.split(':')[0],int(ip.split(':')[1]))
            r.hset(self.recurso,self.sock.id_10,self.socket)

        else:
            r.hset(self.recurso,self.sock.id_10,self.socket)

    def leave(self):

        r.hdel(self.recurso,self.sock.id_10)
        self.sock.unjoin()
        return "Bye"
    
    def get_tracker_list(self):
        tracker_list = list(r.hgetall(self.recurso))
        return tracker_list


    def update(self):
        if self.sock:
            if self.sock.routing_table == {}:
                nodos = self.get_tracker_list()
                nodos_ip = [r.hget(self.recurso,x.decode("utf8")).decode("utf8") for x in nodos]
                for nid in nodos_ip:
                    self.sock.connect(nid.split(':')[0],int(nid.split(':')[1]))
            self.successor = self.sock.next.id
            self.predecessor = self.sock.prev.id
        return f"ID: {self.sock.id}\nSucesor: {self.sock.prev.id}\nPredecesor: {self.sock.next.id}"

def main():
    nodo = Node(ip,int(sys.argv[2]),sys.argv[3])
    nodo.join()
    option = input("[1]-Actualizar nodo\n[2]-Listar datos del nodo\n[3]-Añadir datos\n[4]-Eliminar datos\n[5]-Buscar datos\n[6]-Abandonar la red\n Introduce tu opción: ")
    while True:
        match option:   
            case "1":
                os.system("clear")
                nodo.update()
                print(f"ID: {nodo.sock.id}\nSucesor: {nodo.sock.prev.id}\nPredecesor: {nodo.sock.next.id}\nDatos almacenados: {nodo.data}")
            case "2":
                os.system("clear")
                print(f"Datos del nodo {nodo.data}")
            case "3":
                os.system("clear")
                clave = input("Introduce la clave: ")
                valor = input("Introduce el valor: ")
                nodo.data[clave]=valor
                nodo.sock[clave]=valor
            case "4":
                os.system("clear")
                clave = input("Introduce la clave: ")
                if clave in nodo.data:
                    del nodo.data[clave]
                    del nodo.sock[clave]
                else:
                    print("ERROR: Esa clave no se encuentra almacenada.")
            case "5":
                os.system("clear")
                clave = input("Introduce la clave: ")
                if clave in nodo.data:
                    print(f"El valor de la clave {clave} es {nodo.data[clave]}\n")
                else:
                    try:
                        print(f"El valor de la clave {clave} es {nodo.sock[clave]}\n")
                    except:
                        print("ERROR: No existe valor para la clave indicada.")
            case "6":
                nodo.leave()
                return "Abandonando la red..."
            case _:
                print("ERROR: El valor introducido no es válido.")
        
        option = input("[1]-Actualizar nodo\n[2]-Listar datos del nodo\n[3]-Añadir datos\n[4]-Eliminar datos\n[5]-Buscar datos\n[6]-Abandonar la red\n Introduce tu opción: ")
if __name__ == '__main__':
    main()
