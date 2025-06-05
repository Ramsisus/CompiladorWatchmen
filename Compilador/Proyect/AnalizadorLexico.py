# Importar módulo lex
import ply.lex as lex

# Definir dos variables para los errores
errores_Desc = []
lista_errores_lexicos = []

# Definir método para vaciar listas
def limpiar_errores_lex():
    global errores_Desc
    global lista_errores_lexicos
    errores_Desc = []
    lista_errores_lexicos = []

# Lista de tokens
tokens = [
    # Operadores y símbolos generales
    'SUMA', 'RESTA', 'DIVISION', 'MULTIPLICACION', 'ASIGNACION', 'IGUAL', 'DIFERENTE', 
    'MAYORQUE', 'MENORQUE', 'MENORIGUAL', 'MAYORIGUAL', 
    'PUNTO', 'COMA', 'PUNTOCOMA', 'COMILLASIMPLE', 'COMILLADOBLE', 
    'PARENTESIS_A', 'PARENTESIS_B', 'LLAVE_A', 'LLAVE_C', 
    'CORCHETE_A', 'CORCHETE_B', 'MASMAS', 'MENOSMENOS', 'AND', 'OR', 'NOT',

    # Palabras reservadas y comandos específicos del robot
    'BEGIN', 'END', 'TRUE', 'FALSE', 'IMPORT', 'FUN', 'FROM', 
    'WHILE', 'FOR', 'IF', 'ELSE', 'RETURN', 
    'INT', 'BOOL', 'STG', 'REAL',  # Tipos de datos

    # Comandos del robot vigilante
    'MOVE_TO', 'WAIT_MOTION', 'STOP', 'LIGHT_ON', 'LIGHT_OFF',
    'START_RECORD', 'STOP_RECORD', 'ALARM_ON', 'ALARM_OFF', 'SENSOR_PIR',

    # Identificadores y literales
    'ID', 'NUMERO', 'REAL_LIT', 'CADENA'
]

# Palabras reservadas
reservadas = {
    'begin': 'BEGIN',
    'end': 'END',
    'for': 'FOR',
    'while': 'WHILE',
    'if': 'IF',
    'else': 'ELSE',
    'int': 'INT',
    'real': 'REAL',
    'bool': 'BOOL',
    'stg': 'STG',
    'fun': 'FUN',
    'true': 'TRUE',
    'false': 'FALSE',

    # Comandos del robot vigilante
    'move_to': 'MOVE_TO',
    'wait_motion': 'WAIT_MOTION',
    'stop': 'STOP',
    'light_on': 'LIGHT_ON',
    'light_off': 'LIGHT_OFF',
    'start_record': 'START_RECORD',
    'stop_record': 'STOP_RECORD',
    'alarm_on': 'ALARM_ON',
    'alarm_off': 'ALARM_OFF',
    'sensor_pir': 'SENSOR_PIR'
}

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Definición de tokens simples
t_SUMA = r'\+'
t_RESTA = r'-'
t_DIVISION = r'/'
t_MULTIPLICACION = r'\*'
t_ASIGNACION = r'='
t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MAYORQUE = r'>'
t_MENORQUE = r'<'
t_MENORIGUAL = r'<='
t_MAYORIGUAL = r'>='
t_PUNTO = r'\.'
t_COMA = r','
t_PUNTOCOMA = r';'
t_COMILLASIMPLE = r'\''
t_COMILLADOBLE = r'\"'
t_PARENTESIS_A = r'\('
t_PARENTESIS_B = r'\)'
t_LLAVE_A = r'\{'
t_LLAVE_C = r'\}'
t_CORCHETE_A = r'\['
t_CORCHETE_B = r'\]'
t_MASMAS = r'\+\+'
t_MENOSMENOS = r'--'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

# Identificadores y palabras reservadas
#OSCAR
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_lower = t.value.lower()
    t.type = reservadas.get(t_lower, 'ID')
    return t

# Literales numéricos reales
def t_REAL_LIT(t):
    r'\d+\.\d+|\.\d+'
    t.value = float(t.value)
    return t

# Literales numéricos enteros
def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Cadenas encerradas en #
def t_CADENA(t):
    r'\#.*?\#'
    return t

# Comentarios (líneas que inician con //)
def t_COMENTARIO(t):
    r'//.*'
    pass  # No se devuelve token, se ignora

# Conteo de líneas
def t_SALTOLINEA(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
def t_error(t):
    global errores_Desc
    errores_Desc.append(f"Símbolo no válido '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# Método para manejar identificadores no válidos OSCAR 
# def t_IDError(t):
#     r'\d+[a-zA-ZñÑ][a-zA-Z0-9ñÑ]*'
#     global errores_Desc
#     columna = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
#     errores_Desc.append("Identificador NO válido en la línea " + str(t.lineno) + ", en columna " + str(columna))

# Método para identificar identificadores OSCAR
# def t_IDENTIFICADOR(t): 
#     r'[a-zA-Z][a-zA-Z0-9_]*'  # Expresión regular para identificadores válidos
#     valor = t.value.lower()  # Convertir el valor del identificador a minúsculas
#     if valor in reservadas:  # Verificar si el identificador es una palabra reservada
#         t.type = valor.upper()  # Asignar el tipo del token a la palabra reservada
#     else: 
#         if any(palabra.startswith(valor) for palabra in reservadas):  # Verificar errores en palabras reservadas mal escritas
#             global errores_Desc
#             columna = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)  # Calcular la columna donde se encuentra el error
#             errores_Desc.append(f"Error léxico: palabra reservada mal escrita '{t.value}' en la línea {t.lineno}, en columna {columna}") 
#         t.type = 'ID'  # Asignar el tipo ID si no es una palabra reservada
#     return t

# Construir el analizador léxico
lexer = lex.lex()

# Función de análisis
def analisis(cadena):
    lexer.input(cadena)
    tokens_encontrados = []
    lexer.lineno = 1
    for tok in lexer:
        columna = tok.lexpos - cadena.rfind('\n', 0, tok.lexpos)
        tokens_encontrados.append((tok.value, tok.type, tok.lineno, columna))
    return tokens_encontrados

# Prueba simple
if __name__ == '__main__':
    codigo_prueba = '''
    int a = 5;
    real b = 3.14;
    move_to(10, 20);
    light_on;
    // Esto es un comentario
    #Mensaje de alerta#
    '''
    resultado = analisis(codigo_prueba)
    for token in resultado:
        print(token)
    if errores_Desc:
        print("Errores léxicos encontrados:")
        for error in errores_Desc:
            print(error)