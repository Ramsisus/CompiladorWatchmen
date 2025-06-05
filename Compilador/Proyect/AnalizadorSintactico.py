#Importar modulo yacc
import ply.yacc as yacc
from AnalizadorLexico import tokens
from AnalizadorLexico import lexer

from graphviz import Source #libreria (graphviz) para generar la imagen del arbol
from PIL import Image #libreria (pillow) para abrir imagen

errores_Sinc_Desc = []

def limpiar_errores():
    global errores_Sinc_Desc
    errores_Sinc_Desc = []

linea = 0

precedence = (
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENORQUE', 'MENORIGUAL', 'MAYORQUE', 'MAYORIGUAL'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION')
)

# gramática inicial
def p_programa(p):
    """ programa : BEGIN bloque_codigo END """
    p[0] = ('programa', p[2])

def p_programa_error(p):
    """ programa : BEGIN bloque_codigo """
    errores_Sinc_Desc.append(f"Falta la etiqueta END al final del programa")

def p_bloque_codigo(p):
    """ bloque_codigo : LLAVE_A lista_declaraciones LLAVE_C """
    p[0] = ("bloque_codigo", p[2])

def p_bloque_codigo_error(p):
    """ bloque_codigo : LLAVE_A lista_declaraciones """
    errores_Sinc_Desc.append(f"Falta el cierre de llave al final del bloque de codigo")

def p_lista_declaraciones(p):
    """
    lista_declaraciones : lista_declaraciones declaracion
                        | lista_declaraciones si
                        | lista_declaraciones mientras
                        | lista_declaraciones for_loop
                        | declaracion
                        | si
                        | mientras
                        | for_loop
    """
    if len(p) == 3:
        p[0] = p[1] + [p[2]]  # Si ya tienes una lista, le agregas un nuevo elemento
    else:
        p[0] = [p[1]]         # Caso base: solo un elemento, crear lista con ese

def p_declaracion(p):
    """ declaracion : tipo ID ASIGNACION expresion PUNTOCOMA """
    p[0] = ('declaracion', p[1], p[2], p[4])

def p_declaracion_error(p):
    """ declaracion : tipo ID ASIGNACION PUNTOCOMA """
    errores_Sinc_Desc.append(f"Falta el valor de la expresion en la declaracion de la variable en la linea {p.lineno(1)}")

def p_declaracion_error1(p):
    """ declaracion : tipo ID ASIGNACION expresion """
    errores_Sinc_Desc.append(f"Error: falta punto y coma en la línea: {p.lineno(2)}")

def p_tipo(p):
    """ tipo : INT
             | BOOL
             | STG
             | REAL """
    p[0] = p[1]

# Expresiones aritméticas y comparativas
def p_expresion_binaria(p):
    '''
    expresion : expresion SUMA expresion
              | expresion RESTA expresion
              | expresion MULTIPLICACION expresion
              | expresion DIVISION expresion
              | expresion MENORQUE expresion
              | expresion MENORIGUAL expresion
              | expresion MAYORQUE expresion
              | expresion MAYORIGUAL expresion
              | expresion IGUAL expresion
              | expresion DIFERENTE expresion
    '''
    p[0] = (p[2], p[1], p[3])

def p_expresion_valores(p):
    """ 
    expresion : PARENTESIS_A expresion PARENTESIS_B
              | NUMERO
              | REAL_LIT
              | CADENA
              | TRUE
              | FALSE
    """
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_si(p):
    """
    si : IF PARENTESIS_A expresion PARENTESIS_B bloque_codigo
       | IF PARENTESIS_A expresion PARENTESIS_B bloque_codigo ELSE bloque_codigo
    """
    if len(p) == 8:
        p[0] = ('IF', p[3], p[5], 'ELSE', p[7])
    else:
        p[0] = ('IF', p[3], p[5])

def p_mientras(p):
    """ mientras : WHILE PARENTESIS_A expresion PARENTESIS_B bloque_codigo """
    p[0] = ('WHILE', p[3], p[5])

def p_for_loop(p):
    """
    for_loop : FOR PARENTESIS_A for_init PUNTOCOMA for_condicion PUNTOCOMA for_actualizacion PARENTESIS_B bloque_codigo
    """
    p[0] = ('FOR', {'init': p[3], 'cond': p[5], 'update': p[7], 'body': p[9]})

def p_for_init(p):
    """
    for_init : tipo ID ASIGNACION expresion
             | ID ASIGNACION expresion
    """
    if len(p) == 5:
        p[0] = ('init', {'tipo': p[1], 'id': p[2], 'valor': p[4]})
    else:
        p[0] = ('init', {'id': p[1], 'valor': p[3]})

def p_for_condicion(p):
    """ for_condicion : expresion """
    p[0] = ('cond', p[1])

def p_for_actualizacion(p):
    """
    for_actualizacion : ID ASIGNACION expresion
                      | ID MASMAS
                      | ID MENOSMENOS
    """
    if len(p) == 4:
        p[0] = ('update', {'id': p[1], 'valor': p[3]})
    else:
        p[0] = ('update', f"{p[1]} {p[2]}")

# Comandos del lenguaje del robot

def p_comando_movimiento(p):
    """ declaracion : MOVE_TO PARENTESIS_A NUMERO COMA NUMERO PARENTESIS_B PUNTOCOMA """
    p[0] = ('MOVE_TO', (p[3], p[5]))

def p_comando_movimiento_error(p):
    """ declaracion : MOVE_TO PARENTESIS_A NUMERO COMA PARENTESIS_B PUNTOCOMA
                    | MOVE_TO PARENTESIS_A COMA NUMERO PARENTESIS_B PUNTOCOMA  
    """
    errores_Sinc_Desc.append(f"Falta un parametro en la instruccion MOVE_TO en la linea {p.lineno(1)}")

def p_comando_espera(p):
    """ declaracion : WAIT_MOTION PARENTESIS_A PARENTESIS_B PUNTOCOMA """
    p[0] = ('WAIT_MOTION',)

def p_comando_espera_error(p):
    """ declaracion : WAIT_MOTION PUNTOCOMA """
    errores_Sinc_Desc.append(f"Faltan los parentesis en WAIT_MOTION en la linea {p.lineno(1)}")

def p_comando_grabacion(p):
    """
    declaracion : START_RECORD PARENTESIS_A PARENTESIS_B PUNTOCOMA
                        | STOP_RECORD PARENTESIS_A PARENTESIS_B PUNTOCOMA
    """
    p[0] = (p[1],)

def p_comando_luz(p):
    """
    declaracion : LIGHT_ON PUNTOCOMA
                        | LIGHT_OFF PUNTOCOMA
    """
    p[0] = (p[1],)

def p_comando_alarma(p):
    """
    declaracion : ALARM_ON PUNTOCOMA
                        | ALARM_OFF PUNTOCOMA
    """
    p[0] = (p[1],)

def p_comando_stop(p):
    """ declaracion : STOP PUNTOCOMA """
    p[0] = ('STOP',)

def p_error_comando_stop(p):
    """ declaracion : STOP """
    errores_Sinc_Desc.append(f"Falta punto y coma en la sentencia STOP, linea {p.lineno(1)}")

def p_error(p):
    if p:
        errores_Sinc_Desc.append(f"Error de sintaxis en la línea {p.lineno} cerca de '{p.value}'")
    else:
        errores_Sinc_Desc.append("Error de sintaxis inesperado: fin de archivo")

# Construir analizador
parser = yacc.yacc()

def arbol (codigo):
    syntax_tree = parser.parse(codigo, lexer=lexer) #aqui se genera el arbol
    #obtiene el codigo de la imagen del arbol a partir del arbol sintáctico
    graphviz_code = tree_to_graphviz(syntax_tree)
    print(graphviz_code) #imprime
    graph = Source(graphviz_code)#se prepara el codigo de la imagen del arbol
    graph.render('arbol', format='png', cleanup=True) #se crea el archivo arbol.png

#Cambiar estas dos lineas para desplegarlo con un boton
    image = Image.open('arbol.png') #se busca la imagen
    image.show()#se muestra la imagen

def tree_to_graphviz(tree, graph_str=None, parent_id=None, node_counter=[0]):
    if graph_str is None:
        graph_str = "digraph G {\n"
    
    current_id = f"node{node_counter[0]}"
    node_counter[0] += 1

    # Nodo actual
    if isinstance(tree, tuple):
        op, *children = tree
        graph_str += f'    {current_id} [label="{op}"];\n'
        
        # Recorrer hijos
        for child in children:
            child_id, graph_str = tree_to_graphviz(child, graph_str, current_id, node_counter)
            graph_str += f'    {current_id} -> {child_id};\n'
    elif isinstance(tree, list):
        graph_str += f'    {current_id} [label="lista"];\n'
        graph_str += f'    {current_id} [label="list"];\n'
        for item in tree:
            child_id, graph_str = tree_to_graphviz(item, graph_str, current_id, node_counter)
            graph_str += f'    {current_id} -> {child_id};\n'
    else:
        # Hoja
        graph_str += f'    {current_id} [label="{tree}"];\n'
    
    if parent_id is None:
        graph_str += "}"
    
    return (current_id, graph_str) if parent_id is not None else graph_str

# Función de prueba
def test_parser(codigo):
    result = parser.parse(codigo)
    print("Resultado del análisis sintáctico:")
    print(result)
    print("Errores sintácticos:")
    print(errores_Sinc_Desc)

# Código de prueba
codigo = ""
test_parser(codigo)
print(errores_Sinc_Desc)
#arbol(codigo)