from heapdict import heapdict
import sys

# Leemos el fichero  mapa1
with open(sys.argv[1] + "/" + sys.argv[2], "r") as f:
    mapa = [line.split() for line in f.read().splitlines()]

# Leemos los tipos de contenedores1
with open(sys.argv[1] + "/" + sys.argv[3], "r") as f:
    contenedores = [line.split() for line in f.read().splitlines()]

print(mapa)
print(contenedores)


def get_disponibles(mapa):
    "Dado un mapa, devuelve por cada pila, la posicion mas profunda a la que se pueden poder contenedores"

    disponible = [-1 for i in range(len(mapa[0]))]
    for profundidad in range(len(mapa)):
        for pila in range(len(mapa[0])):
            if mapa[profundidad][pila] == 'X' and disponible[pila] == -1:
                disponible[pila] = profundidad - 1
    return disponible


def get_nums(contenedores):
    """Dados los contenedores, los clasifica en los grupos N1, N2, R1, R2"""
    nums = [0 for i in range(4)]

    for cont in contenedores:
        if cont[2] == '1':
            if cont[1] == 'S':
                nums[0] += 1
            else:
                nums[2] += 1
        else:
            if cont[1] == 'S':
                nums[1] += 1
            else:
                nums[3] += 1
    return nums


class Estado:
    def __init__(self, mapa, nums, port, espacios, descargados_p1, descargados_p2):
        self.mapa = mapa
        self.num_N1, self.num_N2, self.num_R1, self.num_R2 = nums
        self.port = port
        self.espacios = espacios  # [ , , , , ,] indica la profundidad del primer espacio disponible, que no haya 'X' o que no haya un contendor
        self.hijos = []  # [(Estado, coste, accion)]
        self.descargados_p1 = descargados_p1 # Cantidad de contenedores que aun necesitan ser descargados en el puerto 1
        self.descargados_p2 = descargados_p2 # Cantidad de contenedores que aun necesitan ser descargados en el puerto 2

    def print_Estado(self):
        print(self.mapa)
        print(self.num_N1, self.num_N2, self.num_R1, self.num_R2)
        print(self.port)
        print(self.espacios)

    def getHijos(self):
        self.poner()
        self.mover_barco()
        self.descargar()
        return self.hijos[:]

    def poner(self):
        av = [('N1', self.num_N1), ('N2', self.num_N2), ('R1', self.num_R1), ('R2', self.num_R2)]
        for pila in range(len(self.mapa[0])):
            for cont, num_cont in av:
                mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
                espacios = self.espacios[:]
                if (cont == 'N1' and self.port < 1) or (cont == 'N2' and self.port < 2):
                    if num_cont > 0 and espacios[pila] >= 0:
                        mapa[self.espacios[pila]][pila] = cont
                        espacios[pila] -= 1
                        self.hijos.append((Estado(mapa, [self.num_N1 - int(cont == 'N1'), self.num_N2 - int(cont == 'N2'), self.num_R1, self.num_R2],
                                                  self.port, espacios,self.descargados_p1, self.descargados_p2), 1, 'poner' + cont + '_' + str(pila+1) + '_' + str(espacios[pila] + 2)))

                elif (cont == 'R1' and self.port < 1) or (cont == 'R2' and self.port < 2):
                    if num_cont > 0 and espacios[pila] >= 0 and mapa[self.espacios[pila]][pila] == 'E':
                        mapa[self.espacios[pila]][pila] = cont
                        espacios[pila] -= 1
                        self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1 - int(cont == 'R1'), self.num_R2 - int(cont == 'R2')],
                                                  self.port, espacios, self.descargados_p1, self.descargados_p2), 1, 'poner' + cont + '_' + str(pila+1) + '_' + str(espacios[pila] + 2)))

    def descargar(self):
        if self.port == 1:
            for pila in range(len(self.mapa[0])):
                mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
                espacios = self.espacios[:]
                cont = mapa[self.espacios[pila] + 1][pila]
                if cont == 'N1' or cont == 'N2':
                    mapa[self.espacios[pila]][pila] = 'N'
                    espacios[pila] += 1
                    self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2 + int(cont == 'N2'), self.num_R1,
                                                     self.num_R2],self.port, espacios, self.descargados_p1 - 1, self.descargados_p2),
                                       1, 'descargar' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 1)))

                if cont == 'R1' or cont == 'R2': # FActorizable
                    mapa[self.espacios[pila]][pila] = 'E'
                    espacios[pila] += 1
                    self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1,
                                                     self.num_R2 + int(cont == 'R2')],self.port, espacios, self.descargados_p1 - 1, self.descargados_p2),
                                       1, 'decargar' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 1)))

        if self.port == 2:
            for pila in range(len(self.mapa[0])):
                mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
                espacios = self.espacios[:]
                cont = mapa[self.espacios[pila] + 1][pila]
                if cont == 'N2':
                    mapa[self.espacios[pila]][pila] = 'N'
                    espacios[pila] += 1
                    self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1,
                                                     self.num_R2], self.port, espacios, self.descargados_p1,
                                              self.descargados_p2 - 1),
                                       1, 'descargar' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 1)))

                if cont == 'R2':  # FActorizable
                    mapa[self.espacios[pila]][pila] = 'E'
                    espacios[pila] += 1
                    self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1,
                                                     self.num_R2], self.port, espacios,
                                              self.descargados_p1, self.descargados_p2 -1),
                                       1, 'decargar' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 1)))

    def mover_barco(self):
        mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
        espacios = self.espacios[:]
        if self.port == 0 and (self.num_N1 + self.num_N2 + self.num_R1 + self.num_R2) == 0:
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 1, self.espacios,self.descargados_p1, self.descargados_p2), 1,'mover_p1'))

        if self.port == 1 and (self.num_N2 + self.num_R2) == 0 and self.descargados_p1 == 0:
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 2, self.espacios, self.descargados_p1,self.descargados_p2), 1,'mover_p2'))

    def __eq__(self,other):
        """Muy muy optimizable """
        """ Compara si 2 estados son iguales"""
        for pila in range(len(self.mapa[0])):
            for profundidad in range(len(self.mapa)):
                if self.mapa[profundidad][pila] != other.mapa[profundidad][pila]:
                    return False
        return self.port == other.port

    def __hash__(self):
        return hash(tuple(tuple(l) for l in self.mapa))

num_contenedores = get_nums(contenedores)
inicio = Estado(mapa, num_contenedores, 0, get_disponibles(mapa), num_contenedores[0] + num_contenedores[2], num_contenedores[1] + num_contenedores[3])
goal = Estado(mapa, [0, 0, 0, 0], 2, get_disponibles(mapa), 0, 0)

"""
b = inicio.getHijos()
b = b[0]
c = b[0].getHijos()
c = c[0]
print("---------------------------------")
b[0].print_Estado()
c[0].print_Estado()
print("---------------------------------")"""


def heuristica(arg):
    return 1


def AStart(inicio, goal):
    estadisticas = [0,0,0,0] # [Tiempo total, Costel total, Longitud del plan, Nodos expandidos]
    exito = False

    cerrada = set()
    abierta = heapdict()

    g_cost = {inicio: 0}
    abierta[inicio] = g_cost[inicio] + heuristica(inicio)
    prev = {}  # estado : estado_anterior, accion

    while abierta:
        curr, coste_f = abierta.popitem()

        #if curr == goal:
        #if (curr.num_N1 + curr.num_N2 + curr.num_R1 + curr.num_R2) == 0:
        #if curr.descargados_p1 == 0 :
        #if curr.port == 2:
        if curr.port == 2 and curr.descargados_p2 == 0:
            print("Exito")
            curr.print_Estado()
            moves = []
            while curr != inicio:
                curr, accion = prev[curr]
                moves.append(accion)
            print(moves[::-1])
            exito = True
            break
        else:
            cerrada.add(curr)

        for hijo, coste, accion in curr.getHijos():
            coste_hijo = g_cost[curr] + coste

            if hijo in cerrada:
                continue

            if hijo not in abierta or g_cost[hijo] > coste_hijo:
                g_cost[hijo] = coste_hijo
                abierta[hijo] = coste_hijo + heuristica(hijo)
                prev[hijo] = curr, accion

AStart(inicio,goal)