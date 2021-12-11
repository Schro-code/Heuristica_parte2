from heapdict import heapdict
import sys
import time

'''------------------------------Modelizacion del Estado del problema --------------'''

class Estado:
    """Definicio de Estado en nuestro el problema de los contenedores"""
    def __init__(self, mapa, nums, port, espacios, descargados_p1, descargados_p2):
        self.mapa = mapa
        self.num_N1, self.num_N2, self.num_R1, self.num_R2 = nums  # Cantidad de contenedores que necesitan ser cargados en el barco
        self.port = port
        self.espacios = espacios  # [ , , , , ,] indica la profundidad del primer espacio disponible, que no haya 'X' o que no haya un contendor
        self.hijos = []  # [(Estado, coste, accion)]
        self.descargados_p1 = descargados_p1  # Cantidad de contenedores que aun necesitan ser descargados en el puerto 1
        self.descargados_p2 = descargados_p2  # Cantidad de contenedores que aun necesitan ser descargados en el puerto 2

    def print_Estado(self):
        print(self.mapa)
        print(self.num_N1, self.num_N2, self.num_R1, self.num_R2)
        print(self.port)
        print(self.espacios)
        print(self.descargados_p1, self.descargados_p2)
        print('----------------')

    def print_mapa(self):
        for l in self.mapa:
            print(l)

        print("---------")

    def getHijos(self):
        self.poner()
        self.mover_barco()
        self.descargar()
        return self.hijos[:]

    def poner(self):
        ''' Ponemos en cada pila, un contenedor si es posible'''
        av = [('N1', self.num_N1), ('N2', self.num_N2), ('R1', self.num_R1), ('R2', self.num_R2)]

        #Por cada pila compruebo si puedo poner cada tipo de contenedor distinto N1, N2, R1, R2
        for pila in range(len(self.mapa[0])):
            for cont, num_cont in av[::-1]:
                mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
                espacios = self.espacios[:]

                # Si hay contenedores y en la pila existe una posicion disponible
                # Si es un contenedor R la posicion debe ser E
                # Si estamos en el puerto 0 se cargan todos los contenedores, en el puerto 1 se cargan 2
                if (num_cont > 0 and espacios[pila] >= 0 ) and \
                        (((cont == 'N1' or (cont == 'R1' and mapa[self.espacios[pila]][pila] == 'E')) and self.port < 1) or \
                         ((cont == 'N2' or (cont == 'R2' and mapa[self.espacios[pila]][pila] == 'E')) and self.port < 2)):

                    mapa[self.espacios[pila]][pila] = cont
                    espacios[pila] -= 1
                    #Creamos el nuevo estado hijo, se añade  (Estado, coste, accion)
                    self.hijos.append((Estado(mapa,
                                              [self.num_N1 - int(cont == 'N1'), self.num_N2 - int(cont == 'N2'),self.num_R1 - int(cont == 'R1'), self.num_R2 - int(cont == 'R2')],
                                              self.port, espacios, self.descargados_p1, self.descargados_p2),
                                       10 + (espacios[pila] + 1),
                                       'poner_' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 2)))



    def descargar(self):
        if self.port == 1 or self.port == 2:
            for pila in range(len(self.mapa[0])):
                mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
                espacios = self.espacios[:]

                pos_in_pila = self.espacios[pila] + 1
                if self.espacios[pila] + 1 < len(self.mapa):
                    cont = mapa[self.espacios[pila] + 1][pila]
                else:
                    cont = 'fuera del mapa'

                if cont == 'N1' or cont == 'N2' or cont == 'R1' or cont == 'R2':
                    if cont == 'N1' or cont == 'N2':
                        mapa[self.espacios[pila] + 1][pila] = 'N'

                    if cont == 'R1' or cont == 'R2':
                        mapa[self.espacios[pila] + 1][pila] = 'E'
                    espacios[pila] += 1
                    self.hijos.append((Estado(mapa,
                                              [self.num_N1, self.num_N2 + int(cont == 'N2' and self.port == 1),
                                                self.num_R1, self.num_R2 + int(cont == 'R2' and self.port == 1)],
                                              self.port, espacios,
                                              self.descargados_p1 - int((cont == 'R1' or cont == 'N1') and self.port == 1),
                                              self.descargados_p2 - int((cont == 'R2' or cont == 'N2') and self.port == 2)),
                                       15 + 2 * (espacios[pila]),
                                       'descargar_' + cont + '_' + str(pila + 1) + '_' + str(espacios[pila] + 1)))



    def mover_barco(self):
        """Movemos el barco"""
        mapa = [line[:] for line in self.mapa]  # cuidado con los pnteros
        #Si el puerto es 1 y no hay ningun contenedores N1, N2, R1, R2 restante por poner
        if self.port == 0 and (self.num_N1 + self.num_N2 + self.num_R1 + self.num_R2) == 0:
            #Añadimos nuevo hijo  (Estado, coste, accion)
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 1, self.espacios,
                                      self.descargados_p1, self.descargados_p2), 3500, 'mover_barco_p0_p1'))

        # Si el puerto es 1 y no hay ningun contenedores  N2, R2 restante por poner
        if self.port == 1 and (self.num_N2 + self.num_R2) == 0 and self.descargados_p1 == 0:

            #Añadimos nuevo hijo  (Estado, coste, accion)
            self.hijos.append((Estado(mapa, [self.num_N1, self.num_N2, self.num_R1, self.num_R2], 2, self.espacios,
                                      self.descargados_p1, self.descargados_p2), 3500, 'mover_barco_p1_p2'))

    def __eq__(self, other):
        """Muy muy optimizable """
        """ Compara si 2 estados son iguales"""
        for pila in range(len(self.mapa[0])):
            for profundidad in range(len(self.mapa)):
                if self.mapa[profundidad][pila] != other.mapa[profundidad][pila]:
                    return False
        return self.port == other.port

    def __hash__(self):
        return hash(tuple(tuple(l) for l in self.mapa))



'''------------------------------Heuristicas y A* --------------'''
def heuristica(estado,opcion):
    # 0 es para amplitud
    heuristicas = {"amplitud": 0, "heuristica1": heuristica1(estado), "heuristica2": heuristica2(estado)}
    return heuristicas[opcion]

def heuristica1(estado):
    '''Heuristica adminisible, ignora el coste de recolocacion'''

    acc = 0
    if estado.descargados_p2 > 0:
        acc += 3500 * (2 - estado.port) # Necesita ir al puerto 2
    else:
        acc += 3500 * (1 - estado.port)  # Solo necesita ir al puerto 1

    if estado.port == 0:
        # En el puerto 0 el coste sera los que hay que cargar mas lo que hay que descargar
        acc += (estado.num_N1 + estado.num_N2 + estado.num_R1 + estado.num_R2) * 10
    if estado.port <= 1:
        # En el puerto 1 el coste sera los que hay que cargar para el puerto 2 y lo que hay que descargar
        acc += (estado.num_N2 + estado.num_R2) * 10
    if estado.port <= 2:
        acc += (estado.descargados_p2 + estado.descargados_p2) * 15
    return acc

def heuristica2(estado):
    '''Heuristica no adminisible, supone que en los puerto 1 y 2 hay que descargar siempre TODOS los contenedores'''

    acc = 0
    if estado.descargados_p2 > 0:
        acc += 3500 * (2 - estado.port)  # Necesita ir al puerto 2
    else:
        acc += 3500 * (1 - estado.port)  # Solo necesita ir al puerto 1

    if estado.port == 0:
        # Ee el puerto 0 hay que ir al puerto 1, descargar todos los contenedores y colocarlos, ir al puerto 2 y descargar los contenedores restantes
        acc += (estado.num_N1 + estado.num_N2 + estado.num_R1 + estado.num_R2) * 10 # Coste de los que faltan por cargar

    if estado.port <= 1:
        acc += (estado.descargados_p1 + estado.descargados_p1 + estado.descargados_p2 + estado.descargados_p2) * 15  # Descagar en el puerto 1
        acc += (estado.num_N2 + estado.num_R2) * 10  # Cargar los que van al puerto 2

    if estado.port <= 2:
        acc += (estado.descargados_p2 + estado.descargados_p2) * 15 # Descargar los que van al puerto 2
    return acc


def AStart(inicio,opcion):
    estadisticas = {'Tiempo total': time.time(), 'Coste_total': 0, 'Longitud del plan': 0,
                    'Nodos expandidos': 0}  # [Tiempo total, Costel total, Longitud del plan, Nodos expandidos]
    exito = False

    cerrada = set()  # Lista cerrada con los nodos expandidos
    abierta = heapdict()  # Lista de prioridad con los nodos generados

    g_cost = {inicio: 0}  # coste acumulado hasta el nodo
    abierta[inicio] = g_cost[inicio] + heuristica(inicio, opcion)
    prev = {}  # estado : estado_anterior, accion, coste_accion
    while abierta:
        curr, coste_f = abierta.popitem()
        # if curr == goal:
        #if (curr.num_N1 + curr.num_N2 + curr.num_R1 + curr.num_R2) == 0:
        # if curr.descargados_p1 == 0:
        #if curr.port == 2:
        #if curr.port == 2 and curr.descargados_p2 == 0:
        if (curr.descargados_p2 + curr.descargados_p1) == 0:
            moves = []
            estadisticas['Coste_total'] = g_cost[curr]
            while curr != inicio:
                estadisticas['Longitud del plan'] += 1
                curr, accion = prev[curr]
                moves.append(accion)
            estadisticas['Tiempo total'] = time.time() - estadisticas['Tiempo total']
            return moves[::-1], estadisticas
        else:
            cerrada.add(curr)

        estadisticas['Nodos expandidos'] += 1
        for hijo, coste, accion in curr.getHijos():
            coste_hijo = g_cost[curr] + coste

            if hijo in cerrada:  # el hijo ya ha sido expandido
                continue

            if hijo not in abierta or g_cost[hijo] > coste_hijo:  # no ha sido expandido o el coste es menor

                g_cost[hijo] = coste_hijo
                abierta[hijo] = coste_hijo + heuristica(hijo, opcion)
                prev[hijo] = curr, accion
    return [[],[]]


'''------------------------------Funciones auxiliares  --------------'''

def get_disponibles(mapa):
    "Dado un mapa, devuelve por cada pila, la posicion mas profunda a la que se pueden poder contenedores"

    disponible = [-2 for i in range(len(mapa[0]))]
    for profundidad in range(len(mapa)):
        for pila in range(len(mapa[0])):

            if mapa[profundidad][pila] == 'X' and disponible[pila] == -2:
                disponible[pila] = profundidad - 1

            if profundidad == (len(mapa) - 1) and disponible[pila] == -2:
                disponible[pila] = len(mapa) - 1

    return disponible


def get_nums(contenedores):
    """Dados los contenedores, los clasifica en los grupos N1, N2, R1, R2"""
    '''e.g contenedores =[['1', 'S', '2'], ['2', 'S', '1'], ['3', 'S', '2'], ['4', 'R', '1'], ['5', 'R', '2']]
        return [1, 2, 1, 1] '''

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


def parse_solution(solucion):
    ''' Devuelve la soucion para escribirl en el fichero
    e.g  solucion = ['poner_N1_1_1',  'mover_barco_p0_p1']
     return [1. <poner> (N1, (1,1)), 2. <mover> (p0,p1), 8. <descargar> (N1, (1,1))]'''

    acciones = []
    orden = 0
    for linea in solucion:
        orden += 1
        op, cont, x, y = linea.split('_')
        if op == 'mover':
            acciones.append(f"{orden}. <{op}> ({x},{y})")
        else:
            acciones.append(f"{orden}. <{op}> ({cont}, ({x},{y}))")
    return acciones




'''------------------------------Resolucion del problema  --------------'''

# Leemos el fichero  mapa
with open(sys.argv[1] + "/" + sys.argv[2], "r") as f:
    mapa = [line.split() for line in f.read().splitlines()]

# Leemos los tipos de contenedores
with open(sys.argv[1] + "/" + sys.argv[3], "r") as f:
    contenedores = [line.split() for line in f.read().splitlines()]

opcion = sys.argv[4]  # seleccion de heuristica

num_contenedores = get_nums(contenedores)

#Estado(mapa, num_contenedores = [ N1, N2, R1, R2], puerto, posi_pila_dis = [ , , ,], num de cont a p1, num de cont a p2)
inicio = Estado(mapa, num_contenedores, 0, get_disponibles(mapa), num_contenedores[0] + num_contenedores[2],
                num_contenedores[1] + num_contenedores[3])

solucion, estadisticas = AStart(inicio,opcion)
s = parse_solution(solucion)  # Parseamos la solucion para escribirla


"""Escribimos el fichero con la solucion del problema"""
with open(sys.argv[1] + "/" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[4] + ".output", 'w') as f:
    for line in s:
        f.write(line + "\n")

"""Escribimos el fichero con las estadisticas"""
with open(sys.argv[1] + "/" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[4] + ".stat", 'w') as f:
    for key in estadisticas:
        f.write(key + " : " + str(estadisticas[key]) + "\n")
