"""
==========================================================================
 SISTEMA DE TURNOS HOSPITALARIOS
 Trabajo Final Integrador - Laboratorio de Python
 Algoritmos y Estructuras de Datos - ISI - Ciclo 2026
==========================================================================

Descripción general:
Este programa permite administrar la atención de pacientes dentro de un
centro de salud. Contempla:
    - Registro de pacientes.
    - Asignación de turnos por especialidad médica.
    - Clasificación de prioridad según urgencia.
    - Control de disponibilidad de turnos (cupos por especialidad).
    - Atención de pacientes (por orden de prioridad y llegada).
    - Estadísticas básicas de atención diaria.
    - Validación de datos ingresados y manejo básico de errores.

El programa se ejecuta enteramente por consola mediante un menú principal.
==========================================================================
"""

import datetime

# ==========================================================================
# DATOS / ESTRUCTURAS GLOBALES
# ==========================================================================

# Especialidades disponibles: clave -> (nombre especialidad, cupo diario)
ESPECIALIDADES = {
    "1": {"nombre": "Clínica General", "cupo_diario": 15},
    "2": {"nombre": "Pediatría", "cupo_diario": 10},
    "3": {"nombre": "Cardiología", "cupo_diario": 8},
    "4": {"nombre": "Traumatología", "cupo_diario": 8},
    "5": {"nombre": "Ginecología", "cupo_diario": 8},
}

# Prioridades disponibles: clave -> (nombre, peso para ordenar - menor = más urgente)
PRIORIDADES = {
    "1": {"nombre": "Urgente", "peso": 1},
    "2": {"nombre": "Moderada", "peso": 2},
    "3": {"nombre": "Leve", "peso": 3},
}

# Listas principales del sistema (en memoria)
pacientes = []   # lista de diccionarios de pacientes registrados
turnos = []      # lista de diccionarios de turnos asignados

# Contadores / acumuladores globales para estadísticas
contador_turnos_totales = 0
contador_atendidos = 0
acumulador_por_especialidad = {}   # {"Clínica General": cantidad, ...}
acumulador_por_prioridad = {}      # {"Urgente": cantidad, ...}


# ==========================================================================
# FUNCIONES DE VALIDACIÓN (manejo de errores y validaciones de datos)
# ==========================================================================

def leer_entero(mensaje, minimo=None, maximo=None):
    """Solicita un número entero al usuario, validando el rango si corresponde.
    Maneja errores de conversión (ValueError) mediante try/except."""
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"  -> Error: el valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  -> Error: el valor debe ser menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("  -> Error: debe ingresar un número entero válido.")


def leer_texto_no_vacio(mensaje):
    """Solicita una cadena de texto que no puede quedar vacía."""
    while True:
        entrada = input(mensaje).strip()
        if entrada == "":
            print("  -> Error: el campo no puede quedar vacío.")
        elif not all(c.isalpha() or c.isspace() for c in entrada):
            print("  -> Error: el campo solo puede contener letras y espacios.")
        else:
            return entrada.title()


def leer_dni():
    """Solicita un DNI, validando que sea numérico y de longitud razonable."""
    while True:
        entrada = input("DNI del paciente: ").strip()
        if not entrada.isdigit():
            print("  -> Error: el DNI debe contener solo números.")
        elif len(entrada) < 6 or len(entrada) > 9:
            print("  -> Error: el DNI debe tener entre 6 y 9 dígitos.")
        else:
            return entrada


def leer_opcion_de_diccionario(mensaje, diccionario):
    """Valida que la opción ingresada exista dentro de un diccionario de opciones
    (usado tanto para especialidades como para prioridades)."""
    while True:
        entrada = input(mensaje).strip()
        if entrada in diccionario:
            return entrada
        print("  -> Error: opción inválida, intente nuevamente.")


# ==========================================================================
# FUNCIONES DE REGISTRO DE PACIENTES
# ==========================================================================

def buscar_paciente_por_dni(dni):
    """Recorre la lista de pacientes y devuelve el paciente si ya existe."""
    for paciente in pacientes:
        if paciente["dni"] == dni:
            return paciente
    return None


def registrar_paciente():
    """Registra un nuevo paciente validando que el DNI no esté repetido."""
    print("\n--- REGISTRO DE PACIENTE ---")
    dni = leer_dni()

    if buscar_paciente_por_dni(dni) is not None:
        print("  -> Este paciente ya se encuentra registrado.")
        return buscar_paciente_por_dni(dni)

    nombre = leer_texto_no_vacio("Nombre y apellido: ")
    edad = leer_entero("Edad: ", minimo=0, maximo=120)

    nuevo_paciente = {"dni": dni, "nombre": nombre, "edad": edad}
    pacientes.append(nuevo_paciente)
    print(f"  -> Paciente {nombre} registrado correctamente.")
    return nuevo_paciente


def seleccionar_o_registrar_paciente():
    """Permite elegir un paciente ya registrado por DNI, o registrar uno nuevo
    si todavía no existe en el sistema."""
    dni = leer_dni()
    paciente = buscar_paciente_por_dni(dni)
    if paciente is not None:
        print(f"  -> Paciente encontrado: {paciente['nombre']} ({paciente['edad']} años).")
        return paciente

    print("  -> El paciente no está registrado. Complete sus datos:")
    nombre = leer_texto_no_vacio("Nombre y apellido: ")
    edad = leer_entero("Edad: ", minimo=0, maximo=120)
    nuevo_paciente = {"dni": dni, "nombre": nombre, "edad": edad}
    pacientes.append(nuevo_paciente)
    print(f"  -> Paciente {nombre} registrado correctamente.")
    return nuevo_paciente


# ==========================================================================
# FUNCIONES DE GESTIÓN DE TURNOS
# ==========================================================================

def mostrar_especialidades():
    print("\nEspecialidades disponibles:")
    for clave, datos in ESPECIALIDADES.items():
        ocupados = acumulador_por_especialidad.get(datos["nombre"], 0)
        disponibles = datos["cupo_diario"] - ocupados
        print(f"  {clave}. {datos['nombre']} (turnos disponibles hoy: {disponibles})")


def mostrar_prioridades():
    print("\nNiveles de prioridad:")
    for clave, datos in PRIORIDADES.items():
        print(f"  {clave}. {datos['nombre']}")


def hay_disponibilidad(nombre_especialidad):
    """Controla la disponibilidad de turnos para una especialidad según su cupo diario."""
    ocupados = acumulador_por_especialidad.get(nombre_especialidad, 0)
    for datos in ESPECIALIDADES.values():
        if datos["nombre"] == nombre_especialidad:
            return ocupados < datos["cupo_diario"]
    return False


def asignar_turno():
    """Asigna un turno a un paciente, validando disponibilidad de cupos
    para la especialidad elegida."""
    global contador_turnos_totales

    print("\n--- ASIGNACIÓN DE TURNO ---")
    paciente = seleccionar_o_registrar_paciente()

    mostrar_especialidades()
    clave_especialidad = leer_opcion_de_diccionario(
        "Seleccione la especialidad (número): ", ESPECIALIDADES
    )
    especialidad = ESPECIALIDADES[clave_especialidad]["nombre"]

    if not hay_disponibilidad(especialidad):
        print(f"  -> No hay turnos disponibles para {especialidad} en el día de hoy.")
        return

    mostrar_prioridades()
    clave_prioridad = leer_opcion_de_diccionario(
        "Seleccione el nivel de urgencia (número): ", PRIORIDADES
    )
    prioridad = PRIORIDADES[clave_prioridad]["nombre"]
    peso_prioridad = PRIORIDADES[clave_prioridad]["peso"]

    contador_turnos_totales += 1
    turno = {
        "id": contador_turnos_totales,
        "paciente": paciente,
        "especialidad": especialidad,
        "prioridad": prioridad,
        "peso_prioridad": peso_prioridad,
        "estado": "Pendiente",
        "hora_asignacion": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    turnos.append(turno)

    acumulador_por_especialidad[especialidad] = acumulador_por_especialidad.get(especialidad, 0) + 1
    acumulador_por_prioridad[prioridad] = acumulador_por_prioridad.get(prioridad, 0) + 1

    print(f"  -> Turno N° {turno['id']} asignado a {paciente['nombre']} "
          f"({especialidad} - Prioridad {prioridad}).")


def listar_turnos_pendientes():
    """Muestra los turnos pendientes ordenados por prioridad y orden de llegada."""
    pendientes = [t for t in turnos if t["estado"] == "Pendiente"]

    if not pendientes:
        print("\nNo hay turnos pendientes en este momento.")
        return

    pendientes_ordenados = sorted(pendientes, key=lambda t: (t["peso_prioridad"], t["id"]))

    print("\n--- TURNOS PENDIENTES (ordenados por prioridad) ---")
    for turno in pendientes_ordenados:
        print(f"  Turno N°{turno['id']} | Paciente: {turno['paciente']['nombre']} "
              f"(DNI {turno['paciente']['dni']}) | Especialidad: {turno['especialidad']} "
              f"| Prioridad: {turno['prioridad']} | Hora: {turno['hora_asignacion']}")


def atender_siguiente_turno():
    """Atiende al siguiente paciente según prioridad (urgente primero) y,
    entre pacientes de igual prioridad, respeta el orden de llegada (FIFO)."""
    global contador_atendidos

    pendientes = [t for t in turnos if t["estado"] == "Pendiente"]
    if not pendientes:
        print("\n  -> No hay pacientes en espera para atender.")
        return

    siguiente = min(pendientes, key=lambda t: (t["peso_prioridad"], t["id"]))
    siguiente["estado"] = "Atendido"
    contador_atendidos += 1

    print(f"\n  -> Atendiendo turno N°{siguiente['id']}: "
          f"{siguiente['paciente']['nombre']} - {siguiente['especialidad']} "
          f"(Prioridad {siguiente['prioridad']}).")


def buscar_turno_por_id():
    """Permite buscar un turno específico ingresando su número de identificación."""
    if not turnos:
        print("\n  -> Todavía no se registraron turnos.")
        return

    id_turno = leer_entero("Ingrese el número de turno a buscar: ", minimo=1)
    for turno in turnos:
        if turno["id"] == id_turno:
            print(f"\n  Turno N°{turno['id']} | Paciente: {turno['paciente']['nombre']} "
                  f"| Especialidad: {turno['especialidad']} | Prioridad: {turno['prioridad']} "
                  f"| Estado: {turno['estado']}")
            return
    print("  -> No se encontró ningún turno con ese número.")


# ==========================================================================
# ESTADÍSTICAS
# ==========================================================================

def mostrar_estadisticas():
    """Genera estadísticas básicas sobre la atención diaria utilizando
    los acumuladores y contadores globales del sistema."""
    print("\n--- ESTADÍSTICAS DE ATENCIÓN DIARIA ---")
    print(f"Total de turnos asignados: {contador_turnos_totales}")
    print(f"Total de pacientes atendidos: {contador_atendidos}")

    pendientes = contador_turnos_totales - contador_atendidos
    print(f"Total de pacientes en espera: {pendientes}")

    if contador_turnos_totales == 0:
        print("Todavía no hay datos suficientes para generar más estadísticas.")
        return

    print("\nTurnos por especialidad:")
    for especialidad, cantidad in acumulador_por_especialidad.items():
        print(f"  {especialidad}: {cantidad} turno(s)")

    print("\nTurnos por nivel de prioridad:")
    for prioridad, cantidad in acumulador_por_prioridad.items():
        print(f"  {prioridad}: {cantidad} turno(s)")

    porcentaje_atendidos = (contador_atendidos / contador_turnos_totales) * 100
    print(f"\nPorcentaje de turnos atendidos: {porcentaje_atendidos:.1f}%")

    # Especialidad con mayor demanda (acumulador)
    especialidad_top = max(acumulador_por_especialidad, key=acumulador_por_especialidad.get)
    print(f"Especialidad con mayor demanda: {especialidad_top}")


# ==========================================================================
# MENÚ PRINCIPAL
# ==========================================================================

def mostrar_menu():
    print("\n" + "=" * 55)
    print(" SISTEMA DE TURNOS HOSPITALARIOS ".center(55, "="))
    print("=" * 55)
    print("1. Registrar paciente")
    print("2. Asignar turno")
    print("3. Ver turnos pendientes")
    print("4. Atender siguiente paciente")
    print("5. Buscar turno por número")
    print("6. Ver estadísticas del día")
    print("7. Salir")


def main():
    print("Bienvenido/a al Sistema de Turnos Hospitalarios.")

    while True:
        mostrar_menu()
        opcion = leer_entero("Seleccione una opción (1-7): ", minimo=1, maximo=7)

        if opcion == 1:
            registrar_paciente()
        elif opcion == 2:
            asignar_turno()
        elif opcion == 3:
            listar_turnos_pendientes()
        elif opcion == 4:
            atender_siguiente_turno()
        elif opcion == 5:
            buscar_turno_por_id()
        elif opcion == 6:
            mostrar_estadisticas()
        elif opcion == 7:
            print("\nGracias por utilizar el sistema. ¡Hasta pronto!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. ¡Hasta luego!")
