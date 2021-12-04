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
    def __init__(self, mapa, nums, port, espacios):
        self.mapa = mapa
        self.num_N1, self.num_N2, self.num_R1, self.num_R2 = nums
        self.port = port
        self.espacios = espacios  # [ , , , , ,] indica la profundidad del primer espacio disponible, que no haya 'X' o que no haya un contendor
        self.hijos = []  # [(Estado, coste)]

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
                if cont == 'N1' or cont == 'N2':
                    if num_cont > 0 and espacios[pila] >= 0:
                        mapa[self.espacios[pila]][pila] = cont
                        espacios[pila] -= 1
                        self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2 - 1, self.num_R1, self.num_R2],
                                                  self.port, espacios), 1))

                elif cont == 'R1' or cont == 'R2':
                    if num_cont > 0 and espacios[pila] >= 0 and mapa[self.espacios[pila]][pila] == 'E':
                        mapa[self.espacios[pila]][pila] = cont
                        espacios[pila] -= 1
                        self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2 - 1, self.num_R1, self.num_R2],
                                                  self.port, espacios), 1))


    def mover_barco(self):
        if self.port == 0 and (self.num_N1 + self.num_N2 + self.num_R1 + self.num_R2) == 0:
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 1, self.espacios), 1))

        if self.port == 1 and (self.num_N1 + self.num_N2 + self.num_R1 + self.num_R2) == 0:
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 2, self.espacios), 1))

    def __eq__(self,other):
        """Muy muy optimizable """
        """ Compara si 2 estados son iguales"""
        for pila in range(len(self.mapa[0])):
            for profundidad in range(len(self.mapa)):
                if self.mapa[profundidad][pila] != other.mapa[profundidad][pila]:
                    return False
        return self.port == other.port


inicio = Estado(mapa, [1, 2, 1, 1], 0, get_disponibles(mapa))
goal = Estado(mapa, [0, 0, 0, 0], 2, get_disponibles(mapa))

"""
for i, j in inicio.getHijos():
    print("---------------------------------")
    i.print_Estado()
    print("---------------------------------")

"""
def heuristica():
    return 1


def AStart(inicio: Estado, goal: Estado):
    estadisticas = [0,0,0,0] # [Tiempo total, Costel total, Longitud del plan, Nodos expandidos]
    exito = False

    cerrada = set()
    abierta = heapdict()

    g_cost = {inicio: 0}
    abierta[inicio] = g_cost[inicio] + heuristica(inicio)
    prev = {}  # estado : estado_anterior

    while abierta:
        curr, coste_f = abierta.popitem()

        if curr == goal:
            exito = True
            break
        else:
            cerrada.add(curr)

        for hijo, coste in curr.getHijos():
            coste_hijo = g_cost[curr] + coste

            if hijo in cerrada:
                continue

            if hijo not in abierta or g_cost[hijo] > coste_hijo:
                g_cost[hijo] = coste_hijo
                abierta[hijo] = g + heuristica(hijo)
                prev[hijo] = s
