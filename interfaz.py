import tkinter as tk
from tkinter import messagebox
import mysql.connector
import re  # Módulo para validar expresiones regulares (formato de correo)

try:
    cn = mysql.connector.connect(
        user='root',
        password='180507',
        host='127.0.0.1',
        database='quizgen_ia',
        port=3306
    )

    if cn.is_connected():
        print("Conexión exitosa a MySQL")

except mysql.connector.Error as e:
    print(f"Error de conexión: {e}")

cursor = cn.cursor()

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS preguntas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pregunta TEXT NOT NULL,
        opciones TEXT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cn.commit()
except mysql.connector.Error as e:
    print("Error creando tabla preguntas:", e)


TEMAS = {
    "claro": {
        "fondo": "#F5F7FA", "texto": "#2D3436", "primario": "#4A90E2", 
        "barra_nav": "#FFFFFF", "btn_texto": "white", "input_bg": "white"
    },
    "oscuro": {
        "fondo": "#2D3436", "texto": "#F5F7FA", "primario": "#0BC376", 
        "barra_nav": "#1E272E", "btn_texto": "white", "input_bg": "#636E72"
    }
}


class QuizGenIAMovilApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.usuario_id = None  # Se asignará dinámicamente al iniciar sesión
        self.cursor = cn.cursor()
        
        self.title("QuizGen IA")
        self.geometry("360x700") 
        self.resizable(False, False)
        
        self.tema_actual = "claro"
        self.colores = TEMAS[self.tema_actual]

        # --- DATOS ORIGINALES DEL QUIZ (AMPLIADOS) ---
        self.carreras = ["Ing. en Sistemas", "Cuidados P. Dependientes", "Ing. en Mecatronica", "Admin. Hotelera y Gast."]
        self.carrera_seleccionada = tk.StringVar(value=self.carreras[0])
        
        self.banco_preguntas = {
            "Ing. en Sistemas": [
                {"pregunta": "¿Cual es una caracteristica clave del modelo en Cascada?", "opciones": ["Iterativo", "Secuencial", "Continuo", "Extremo"], "respuesta": "Secuencial", "feedback": "Requiere terminar una fase por completo antes de pasar a la siguiente."},
                {"pregunta": "¿Estructura para evaluar casos en Python 3.10+?", "opciones": ["While", "For", "Match-Case", "If-Else"], "respuesta": "Match-Case", "feedback": "Permite evaluar multiples valores de una variable de forma limpia."},
                {"pregunta": "¿Cual de estos es un pilar de la Programacion Orientada a Objetos?", "opciones": ["Encapsulamiento", "Compilacion", "Recursividad", "Iteracion"], "respuesta": "Encapsulamiento", "feedback": "Consiste en ocultar el estado interno del objeto y requerir que toda interaccion se realice a traves de los metodos del objeto."},
                {"pregunta": "¿Que lenguaje se utiliza principalmente para consultar bases de datos relacionales?", "opciones": ["Python", "SQL", "HTML", "C++"], "respuesta": "SQL", "feedback": "Structured Query Language es el estandar para bases de datos relacionales."},
                {"pregunta": "¿Cual es el protocolo principal para transferir paginas web?", "opciones": ["FTP", "SMTP", "HTTP", "SSH"], "respuesta": "HTTP", "feedback": "Hypertext Transfer Protocol es la base de la comunicacion de datos en la World Wide Web."}
            ],
            "Cuidados P. Dependientes": [
                {"pregunta": "¿Objetivo principal de los cambios posturales?", "opciones": ["Evitar ulceras", "Dormir mas", "Reducir apetito", "Aumentar masa"], "respuesta": "Evitar ulceras", "feedback": "Previenen lesiones en la piel por falta de circulacion."},
                {"pregunta": "¿Como actuar ante una persona desorientada?", "opciones": ["Ignorar", "Reorientar", "Sedar", "Aislar"], "respuesta": "Reorientar", "feedback": "La empatia y reorientacion previenen crisis de ansiedad."},
                {"pregunta": "¿Con que frecuencia minima se debe realizar la higiene bucal en un paciente dependiente?", "opciones": ["Una vez a la semana", "Despues de cada comida", "Solo en la mañana", "Cuando lo pida"], "respuesta": "Despues de cada comida", "feedback": "Previene infecciones y mantiene el confort del paciente."},
                {"pregunta": "¿Cual es la temperatura corporal normal en un adulto?", "opciones": ["34-35°C", "36-37.5°C", "38-39°C", "40°C"], "respuesta": "36-37.5°C", "feedback": "Ese es el rango considerado como normotermia en adultos."},
                {"pregunta": "¿Cual es la forma correcta de levantar a una persona encamada?", "opciones": ["Tirando de los brazos", "Doblando la espalda", "Flexionando rodillas y usando peso del cuerpo", "Empujando desde la cabeza"], "respuesta": "Flexionando rodillas y usando peso del cuerpo", "feedback": "Esto protege la espalda del cuidador y es mas seguro para el paciente."}
            ],
            "Ing. en Mecatronica": [
                {"pregunta": "¿Que disciplinas se integran en la Mecatronica?", "opciones": ["Informatica y redes", "Mecanica, electronica y control", "Quimica y biologia", "Administracion"], "respuesta": "Mecanica, electronica y control", "feedback": "Sinergia de estas ramas para sistemas automatizados."},
                {"pregunta": "¿Cual es la funcion de un actuador?", "opciones": ["Procesar datos", "Medir temperatura", "Generar movimiento", "Almacenar datos"], "respuesta": "Generar movimiento", "feedback": "Ejecutan acciones fisicas dictadas por el control."},
                {"pregunta": "¿Cual es la funcion principal de un sensor en un sistema mecatronico?", "opciones": ["Generar energia", "Mover piezas", "Medir variables fisicas", "Enfriar el sistema"], "respuesta": "Medir variables fisicas", "feedback": "Los sensores traducen magnitudes fisicas a señales electricas para el controlador."},
                {"pregunta": "¿Cual de los siguientes es un microcontrolador popular para prototipado?", "opciones": ["Arduino", "Windows", "AutoCAD", "Excel"], "respuesta": "Arduino", "feedback": "Arduino es una plataforma de creacion de electronica de codigo abierto."},
                {"pregunta": "¿Que significa PID en la teoria de control?", "opciones": ["Proporcional Integral Derivativo", "Posicion Interna Directa", "Proceso Inteligente Digital", "Pulso Integrado Doble"], "respuesta": "Proporcional Integral Derivativo", "feedback": "Es un mecanismo de control por retroalimentacion ampliamente usado en sistemas de control industrial."}
            ],
            "Admin. Hotelera y Gast.": [
                {"pregunta": "¿Indicador de rentabilidad de habitaciones?", "opciones": ["Costo receta", "Porcentaje de ocupacion", "Rotacion personal", "Eventos"], "respuesta": "Porcentaje de ocupacion", "feedback": "Relacion entre habitaciones ocupadas y disponibles."},
                {"pregunta": "¿Que significa el sistema PEPS?", "opciones": ["Primeros Entrar Salir", "Productos Especiales", "Precios Estandarizados", "Preparacion Exclusiva"], "respuesta": "Primeros Entrar Salir", "feedback": "Garantiza que lo mas antiguo se use primero para evitar caducidad."},
                {"pregunta": "¿Que departamento se encarga del registro y salida de los huespedes?", "opciones": ["Ama de llaves", "Recepcion", "Mantenimiento", "Recursos Humanos"], "respuesta": "Recepcion", "feedback": "Es el punto de contacto principal y gestiona el check-in y check-out."},
                {"pregunta": "¿Como se llama la tecnica de sumergir alimentos en agua hirviendo y luego en agua helada?", "opciones": ["Freir", "Hornear", "Blanquear", "Asar"], "respuesta": "Blanquear", "feedback": "Sirve para detener la coccion, fijar colores o facilitar el pelado de verduras."},
                {"pregunta": "¿Que es el turismo sostenible?", "opciones": ["Viajar lo mas rapido posible", "Minimizar impacto ambiental y cultural", "Gastar menos dinero", "Visitar solo playas"], "respuesta": "Minimizar impacto ambiental y cultural", "feedback": "Busca un equilibrio entre el visitante, la industria, el medio ambiente y las comunidades locales."}
            ]
        }

        self.preguntas_actuales = []
        self.indice_actual = 0
        self.aciertos = 0
        self.opcion_seleccionada = tk.StringVar()
        
        self.crear_barra_superior()

        self.contenedor = tk.Frame(self, bg=self.colores["fondo"])
        self.contenedor.pack(fill="both", expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        self.frames = {}
        pantallas = (
            PantallaLogin, PantallaRegistro,
            PantallaInicio, PantallaMenu, DashboardPrincipal, CrearQuiz, 
            GeneracionIA, EditorPreguntas, BibliotecaQuizzes, ResolverQuiz, 
            Resultados, Historial, Configuracion, VerPreguntas
        )
        
        for F in pantallas:
            page_name = F.__name__
            frame = F(parent=self.contenedor, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_pantalla("PantallaLogin")

    def crear_barra_superior(self):
        self.top_bar = tk.Frame(self, bg=self.colores["primario"], height=50)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False) 
        
        self.lbl_logo = tk.Label(self.top_bar, text="QuizGen IA", font=("Segoe UI", 14, "bold"), 
                                 bg=self.colores["primario"], fg=self.colores["btn_texto"])
        self.lbl_logo.pack(side="left", padx=15, pady=10)

        self.btn_menu = tk.Button(self.top_bar, text="Menu", font=("Segoe UI", 10, "bold"),
                                  bg=self.colores["primario"], fg="white", relief="flat",
                                  command=self.navegar_al_menu)
        self.btn_menu.pack(side="right", padx=15, pady=10)

    def navegar_al_menu(self):
        if self.usuario_id is None:
            messagebox.showwarning("Acceso denegado", "Por favor inicia sesión primero.")
        else:
            self.mostrar_pantalla("PantallaMenu")

    def mostrar_pantalla(self, nombre_pantalla):
        frame = self.frames[nombre_pantalla]
        frame.tkraise()

    def cambiar_tema(self, nuevo_tema):
        if nuevo_tema not in TEMAS: return
        self.tema_actual = nuevo_tema
        self.colores = TEMAS[self.tema_actual]

        self.top_bar.configure(bg=self.colores["primario"])
        self.lbl_logo.configure(bg=self.colores["primario"], fg=self.colores["btn_texto"])
        self.btn_menu.configure(bg=self.colores["primario"], fg="white")
        self.contenedor.configure(bg=self.colores["fondo"])

        for frame in self.frames.values():
            frame.colores = self.colores 
            self._actualizar_colores_recursivo(frame)

    def _actualizar_colores_recursivo(self, widget):
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.colores["fondo"])
            elif isinstance(widget, tk.Label):
                if widget != getattr(self.frames.get("PantallaLogin"), "lbl_error_correo", None):
                    widget.configure(bg=self.colores["fondo"], fg=self.colores["texto"])
                else:
                    widget.configure(bg=self.colores["fondo"]) # Mantiene color rojo de error
            elif isinstance(widget, tk.Radiobutton):
                widget.configure(bg=self.colores["fondo"], fg=self.colores["texto"], selectcolor=self.colores["fondo"])
            elif isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
                widget.configure(bg=self.colores["input_bg"], fg=self.colores["texto"], insertbackground=self.colores["texto"])
        except tk.TclError:
            pass 
        for hijo in widget.winfo_children():
            self._actualizar_colores_recursivo(hijo)


class PantallaBase(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.colores["fondo"])
        self.controller = controller
        self.colores = controller.colores

    def crear_titulo(self, texto):
        tk.Label(self, text=texto, font=("Segoe UI", 18, "bold"), 
                 bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=(20, 10))

    def crear_boton(self, texto, comando, color="#4A90E2"):
        btn = tk.Button(self, text=texto, font=("Segoe UI", 11, "bold"), bg=color, 
                        fg="white", relief="flat", pady=8, command=comando)
        btn.pack(fill="x", padx=30, pady=5)
        return btn


class PantallaLogin(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Iniciar Sesión")
        
        tk.Label(self, text="Correo electrónico:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=(10, 0))
        self.entrada_correo = tk.Entry(self, font=("Segoe UI", 11))
        self.entrada_correo.pack(fill="x", padx=30, pady=5)
        
        # Etiqueta para mostrar la leyenda "correo electrónico inválido" en la UI
        self.lbl_error_correo = tk.Label(self, text="", font=("Segoe UI", 10, "bold"), bg=self.colores["fondo"], fg="#E74C3C")
        self.lbl_error_correo.pack(pady=(2, 0))
        
        tk.Label(self, text="Contraseña:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=(5, 0))
        self.entrada_pass = tk.Entry(self, font=("Segoe UI", 11), show="*")
        self.entrada_pass.pack(fill="x", padx=30, pady=5)
        
        self.crear_boton("Ingresar", self.verificar_login, "#4A90E2")
        self.crear_boton("Registrarse", lambda: controller.mostrar_pantalla("PantallaRegistro"), "#9B59B6")

    def validar_formato_correo(self, correo):
        # Expresión de coincidencia para estructuras de correo electrónico válidas
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, correo) is not None

    def verificar_login(self):
        correo = self.entrada_correo.get().strip()
        contrasena = self.entrada_pass.get()
        
        self.lbl_error_correo.config(text="") # Limpia errores anteriores
        
        if not correo or not contrasena:
            messagebox.showwarning("Atención", "Por favor llena todos los campos.")
            return
            
        # Comprobación de formato del correo electrónico
        if not self.validar_formato_correo(correo):
            self.lbl_error_correo.config(text="correo electrónico inválido")
            messagebox.showerror("Error de Formato", "Por favor ingresa una dirección de correo electrónico válida.")
            return
            
        try:
            sql = "SELECT id, nombre FROM usuarios WHERE correo = %s AND contrasena = %s"
            cursor.execute(sql, (correo, contrasena))
            usuario = cursor.fetchone()
            
            if usuario:
                self.controller.usuario_id = usuario[0] 
                messagebox.showinfo("Éxito", f"¡Bienvenido(a), {usuario[1]}!")
                
                self.entrada_correo.delete(0, tk.END)
                self.entrada_pass.delete(0, tk.END)
                
                self.controller.mostrar_pantalla("PantallaInicio")
            else:
                messagebox.showerror("Error", "Correo o contraseña incorrectos.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error BD", f"Error de conexión: {e}")


class PantallaRegistro(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Crear Cuenta")
        
        tk.Label(self, text="Nombre completo:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack()
        self.entrada_nombre = tk.Entry(self, font=("Segoe UI", 11))
        self.entrada_nombre.pack(fill="x", padx=30, pady=5)
        
        tk.Label(self, text="Correo electrónico:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack()
        self.entrada_correo = tk.Entry(self, font=("Segoe UI", 11))
        self.entrada_correo.pack(fill="x", padx=30, pady=5)
        
        tk.Label(self, text="Contraseña:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack()
        self.entrada_pass = tk.Entry(self, font=("Segoe UI", 11), show="*")
        self.entrada_pass.pack(fill="x", padx=30, pady=5)
        
        self.crear_boton("Guardar Registro", self.registrar_usuario, "#00B894")
        self.crear_boton("Volver al Login", lambda: controller.mostrar_pantalla("PantallaLogin"), "#E74C3C")

    def registrar_usuario(self):
        nombre = self.entrada_nombre.get()
        correo = self.entrada_correo.get()
        contrasena = self.entrada_pass.get()
        
        if not nombre or not correo or not contrasena:
            messagebox.showwarning("Atención", "Por favor llena todos los campos.")
            return
            
        try:
            sql = "INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, correo, contrasena))
            cn.commit()
            
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            
            self.entrada_nombre.delete(0, tk.END)
            self.entrada_correo.delete(0, tk.END)
            self.entrada_pass.delete(0, tk.END)
            
            self.controller.mostrar_pantalla("PantallaLogin")
            
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Este correo ya está registrado.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error BD", f"Error al registrar: {e}")


class PantallaMenu(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Navegación")
        rutas = {
            "Inicio": "PantallaInicio", "Dashboard": "DashboardPrincipal",
            "Crear Quiz": "CrearQuiz", "Seleccionar Quiz": "BibliotecaQuizzes",
            "Historial": "Historial","Ver Preguntas": "VerPreguntas", "Configuracion": "Configuracion"
        }
        for texto, ruta in rutas.items():
            self.crear_boton(texto, lambda r=ruta: controller.mostrar_pantalla(r), "#34495E")


class PantallaInicio(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Bienvenido Alumn@")
        tk.Label(self, text="¿Que deseas hacer hoy?", font=("Segoe UI", 11), 
                 bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=10)
        self.crear_boton("Crear Quiz", lambda: controller.mostrar_pantalla("CrearQuiz"), "#4A90E2")
        self.crear_boton("Resolver Quiz", lambda: controller.mostrar_pantalla("BibliotecaQuizzes"), "#00B894")
        self.crear_boton("Ver Historial", lambda: controller.mostrar_pantalla("Historial"), "#6C5CE7")


class DashboardPrincipal(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Dashboard")
        tk.Label(self, text="Total creados: 12\nResueltos: 45\nPromedio: 85%", 
                 font=("Segoe UI", 12), bg=self.colores["fondo"], fg=self.colores["texto"], justify="left").pack(pady=20)
        self.crear_boton("Nuevo Quiz", lambda: controller.mostrar_pantalla("CrearQuiz"))


class CrearQuiz(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Crear Quiz")
        tk.Entry(self, font=("Segoe UI", 11)).pack(fill="x", padx=30, pady=5)
        tk.Label(self, text="Materia:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack()
        tk.Entry(self, font=("Segoe UI", 11)).pack(fill="x", padx=30, pady=5)
        self.crear_boton("Generar con IA", lambda: controller.mostrar_pantalla("GeneracionIA"), "#9B59B6")
        self.crear_boton("Crear Manualmente", lambda: controller.mostrar_pantalla("EditorPreguntas"))


class GeneracionIA(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Generar con IA")
        tk.Label(self, text="Pega el texto aqui:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack()
        tk.Text(self, height=5, font=("Segoe UI", 10)).pack(fill="x", padx=30, pady=5)
        self.crear_boton("Generar Preguntas", lambda: messagebox.showinfo("IA", "Generando..."))
        self.crear_boton("Volver", lambda: controller.mostrar_pantalla("CrearQuiz"), "#E74C3C")


class EditorPreguntas(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.crear_titulo("Editor de Preguntas")

        # ---------------- PREGUNTA ----------------
        tk.Label(self, text="Pregunta:",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()

        self.entry_pregunta = tk.Entry(self)
        self.entry_pregunta.pack(fill="x", padx=30, pady=5)

        # ---------------- OPCIONES ----------------
        tk.Label(self, text="Opción A:",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()
        self.op_a = tk.Entry(self)
        self.op_a.pack(fill="x", padx=30, pady=5)

        tk.Label(self, text="Opción B:",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()
        self.op_b = tk.Entry(self)
        self.op_b.pack(fill="x", padx=30, pady=5)

        tk.Label(self, text="Opción C:",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()
        self.op_c = tk.Entry(self)
        self.op_c.pack(fill="x", padx=30, pady=5)

        tk.Label(self, text="Opción D:",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()
        self.op_d = tk.Entry(self)
        self.op_d.pack(fill="x", padx=30, pady=5)

        # ---------------- RESPUESTA ----------------
        tk.Label(self, text="Respuesta correcta (A/B/C/D):",
                 bg=self.colores["fondo"],
                 fg=self.colores["texto"]).pack()

        self.respuesta = tk.Entry(self)
        self.respuesta.pack(fill="x", padx=30, pady=5)

        # ---------------- BOTÓN ----------------
        self.crear_boton(
            "Guardar Pregunta",
            self.guardar_pregunta,
            "#00B894"
        )

    def guardar_pregunta(self):
        pregunta = self.entry_pregunta.get().strip()
        a = self.op_a.get().strip()
        b = self.op_b.get().strip()
        c = self.op_c.get().strip()
        d = self.op_d.get().strip()
        respuesta = self.respuesta.get().strip().upper()

        if not all([pregunta, a, b, c, d, respuesta]):
            messagebox.showwarning("Atención", "Completa todos los campos")
            return

        if respuesta not in ["A", "B", "C", "D"]:
            messagebox.showerror("Error", "Respuesta debe ser A, B, C o D")
            return

        try:
            cursor.execute("""
                INSERT INTO preguntas
                (pregunta, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (pregunta, a, b, c, d, respuesta))

            cn.commit()

            messagebox.showinfo("Éxito", "Pregunta guardada correctamente")

            self.entry_pregunta.delete(0, tk.END)
            self.op_a.delete(0, tk.END)
            self.op_b.delete(0, tk.END)
            self.op_c.delete(0, tk.END)
            self.op_d.delete(0, tk.END)
            self.respuesta.delete(0, tk.END)

        except mysql.connector.Error as e:
            messagebox.showerror("Error MySQL", str(e))

class VerPreguntas(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.crear_titulo("Preguntas Guardadas")

        self.frame_lista = tk.Frame(self, bg=self.colores["fondo"])
        self.frame_lista.pack(fill="both", expand=True)

        self.crear_boton(
            "Actualizar",
            self.cargar_preguntas,
            "#00B894"
        )

        self.cargar_preguntas()

    def cargar_preguntas(self):
        # limpiar pantalla
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        try:
            cursor.execute("SELECT pregunta FROM preguntas")
            preguntas = cursor.fetchall()

            if not preguntas:
                tk.Label(
                    self.frame_lista,
                    text="No hay preguntas aún",
                    bg=self.colores["fondo"],
                    fg=self.colores["texto"]
                ).pack(pady=20)
                return

            for p in preguntas:
                tk.Label(
                    self.frame_lista,
                    text="• " + p[0],
                    bg=self.colores["fondo"],
                    fg=self.colores["texto"],
                    anchor="w",
                    justify="left"
                ).pack(fill="x", padx=20, pady=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))            

class BibliotecaQuizzes(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Selecciona tu Carrera")
        
        tk.Label(self, text="Elige el area de evaluacion:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=10)
        
        menu = tk.OptionMenu(self, controller.carrera_seleccionada, *controller.carreras)
        menu.config(font=("Segoe UI", 11), bg="white", relief="flat", highlightthickness=1)
        menu.pack(fill="x", padx=30, pady=(5, 30))
        
        self.crear_boton("Iniciar Evaluacion", self.preparar_evaluacion, "#00B894")

    def preparar_evaluacion(self):
        carrera = self.controller.carrera_seleccionada.get()
        self.controller.preguntas_actuales = self.controller.banco_preguntas[carrera]
        self.controller.indice_actual = 0
        self.controller.aciertos = 0
        
        self.controller.frames["ResolverQuiz"].mostrar_pregunta()
        self.controller.mostrar_pantalla("ResolverQuiz")


class ResolverQuiz(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller = controller

    def mostrar_pregunta(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.crear_titulo("Quiz")

        # 🔥 cargar preguntas desde BD (solo una vez)
        if not hasattr(self.controller, "preguntas_bd"):
            cursor.execute("SELECT * FROM preguntas")
            self.controller.preguntas_bd = cursor.fetchall()
            self.controller.indice_actual = 0
            self.controller.aciertos = 0

        preguntas = self.controller.preguntas_bd
        i = self.controller.indice_actual

        if i >= len(preguntas):
            self.mostrar_resultado()
            return

        p = preguntas[i]

        id, pregunta, a, b, c, d, respuesta = p

        tk.Label(
            self,
            text=f"Pregunta {i+1}",
            bg=self.colores["fondo"],
            fg=self.colores["texto"]
        ).pack()

        tk.Label(
            self,
            text=pregunta,
            wraplength=300,
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)

        self.var = tk.StringVar()

        opciones = [a, b, c, d]

        for op in opciones:
            tk.Radiobutton(
                self,
                text=op,
                variable=self.var,
                value=op,
                bg=self.colores["fondo"],
                fg=self.colores["texto"],
                selectcolor=self.colores["fondo"]
            ).pack(anchor="w", padx=20)

        self.crear_boton("Responder", self.verificar, "#00B894")

    def verificar(self):
        seleccion = self.var.get()

        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una respuesta")
            return

        p = self.controller.preguntas_bd[self.controller.indice_actual]
        correcta = p[6]

        if seleccion == correcta:
            self.controller.aciertos += 1
            messagebox.showinfo("Correcto", "Respuesta correcta")
        else:
            messagebox.showinfo("Incorrecto", f"La correcta era: {correcta}")

        self.controller.indice_actual += 1
        self.mostrar_pregunta()

    def mostrar_resultado(self):
        for widget in self.winfo_children():
            widget.destroy()

        total = len(self.controller.preguntas_bd)
        aciertos = self.controller.aciertos
        porcentaje = int((aciertos / total) * 100)

        self.crear_titulo("Resultados")

        tk.Label(
            self,
            text=f"Aciertos: {aciertos}/{total}\n{porcentaje}%",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Segoe UI", 14)
        ).pack(pady=20)

        self.crear_boton(
            "Volver al inicio",
            lambda: self.controller.mostrar_pantalla("PantallaInicio"),
            "#4A90E2"
        )


class Resultados(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Resultados")
        
        self.lbl_mensaje = tk.Label(self, font=("Segoe UI", 16, "bold"), bg=self.colores["fondo"], fg="#27AE60")
        self.lbl_mensaje.pack(pady=10)
        
        self.lbl_stats = tk.Label(self, font=("Segoe UI", 12), bg=self.colores["fondo"], fg=self.colores["texto"])
        self.lbl_stats.pack(pady=20)
        
        self.crear_boton("Volver al Inicio", lambda: controller.mostrar_pantalla("PantallaInicio"))

    def actualizar_resultados(self):
        aciertos = self.controller.aciertos
        total = len(self.controller.preguntas_actuales)
        porcentaje = int((aciertos / total) * 100) if total > 0 else 0
        
        self.lbl_mensaje.config(text="Evaluacion Terminada")
        self.lbl_stats.config(text=f"Calificacion: {porcentaje}%\nAciertos: {aciertos} de {total}")

        try: 
            sql = """
            INSERT INTO resultados
            (usuario_id, quiz_id, aciertos, porcentaje)
            VALUES (%s, %s, %s, %s)
            """

            valores = (
                self.controller.usuario_id,
                1,
                aciertos,
                porcentaje
            )

            cursor.execute(sql, valores)
            cn.commit() 

            print("Resultado guardado correctamente")

        except mysql.connector.Error as e: 
            print("Error al guardar:", e)
            messagebox.showerror("Error de Base de Datos", f"Detalle: {e}")


class Historial(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Historial")
        tk.Label(self, text="12/Oct - Ing. Sistemas - 90%\n10/Oct - Mecatronica - 75%", 
                 font=("Segoe UI", 11), bg=self.colores["fondo"], fg=self.colores["texto"], justify="left").pack(pady=20)


class Configuracion(PantallaBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.crear_titulo("Configuracion")
        tk.Label(self, text="Tema dinamico:", bg=self.colores["fondo"], fg=self.colores["texto"]).pack(pady=10)
        self.crear_boton("Tema Claro", lambda: controller.cambiar_tema("claro"), "#0AA6B8")
        self.crear_boton("Tema Oscuro", lambda: controller.cambiar_tema("oscuro"), "#34495E")


if __name__ == "__main__":
    app = QuizGenIAMovilApp()
    app.mainloop()