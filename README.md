# Sistema de Turnos Hospitalarios 🏥
### Trabajo Final Integrador — Laboratorio de Python
**Asignatura:** Algoritmos y Estructuras de Datos — ISI — Ciclo 2026

---

## 👥 Integrantes y Comisión
* **Comisión:** ISI K1.1
* **Integrantes:**
  * Ramirez Gonzalez, Juan Ignacio
  * Sotelo, Joaquin Patricio
  * Sussoni, Bautista Benjamin

---

## 📝 Descripción General del Sistema
Este sistema interactivo por consola permite administrar la atención diaria de pacientes dentro de un centro de salud de manera eficiente, lógica y automatizada.

### Funcionalidades principales:
* **Registro de Pacientes:** Permite dar de alta a nuevos pacientes (DNI, nombre, apellido y edad) validando de forma estricta que no existan duplicados en el sistema.
* **Asignación de Turnos:** Vincula a un paciente (nuevo o ya registrado) con una especialidad médica y un nivel de prioridad, controlando de manera automática el cupo diario disponible por especialidad.
* **Cola de Espera Inteligente:** Ordena automáticamente a los pacientes pendientes utilizando un criterio de urgencia real (según el peso de su prioridad) y, en caso de igual urgencia, por estricto orden de llegada (FIFO).
* **Gestión y Estadísticas:** Permite realizar la atención del siguiente paciente crítico, buscar turnos específicos por ID y visualizar métricas de rendimiento en tiempo real (porcentajes de atención, turnos por sector y especialidad con mayor demanda).

---

## ⚙️ Instrucciones de Ejecución

### Requisitos previos
* Tener instalado **Python 3.x** en el sistema.

### Pasos para ejecutar el programa
1. **Clonar el repositorio** o descargar el archivo de código fuente `sistema_turnos_hospitalarios.py`.
2. Abrir una terminal (consola) y navegar hasta la carpeta donde se encuentra el archivo.
3. Ejecutar el siguiente comando:
   ```bash
   python sistema_turnos_hospitalarios.py
