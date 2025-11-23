import pandas as pd
from utils import FRANJAS, franjas_ocupadas
import unicodedata

DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES"]

def quitar_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def detectar_max_colisiones(df, ciclo, dia):
    """
    Detecta el máximo número de cursos simultáneos en un día.
    """
    df_ciclo = df[df['ciclo'] == ciclo].copy()
    df_ciclo = df_ciclo[df_ciclo['dia'].str.strip().str.upper() == dia]
    
    colisiones = {}
    
    for franja in FRANJAS:
        cursos_en_franja = 0
        for _, row in df_ciclo.iterrows():
            franjas = franjas_ocupadas(row['hora_inicio'], row['hora_fin'])
            if franja in franjas:
                cursos_en_franja += 1
        colisiones[franja] = cursos_en_franja
    
    max_colisiones = max(colisiones.values()) if colisiones else 1
    return max_colisiones, colisiones

def crear_horario_ciclo(df, ciclo):
    """
    Crea un horario con subcolunas dinámicas.
    GARANTIZA que cada curso mantenga su subcolumna en TODAS sus franjas.
    
    Retorna: (df_horario, max_colisiones_por_dia, franjas_activas)
    """
    df_ciclo = df[df['ciclo'] == ciclo].copy()
    
    # Calcular máximo de colisiones por día
    max_colisiones_por_dia = {}
    for dia in DIAS:
        max_col, _ = detectar_max_colisiones(df, ciclo, dia)
        max_colisiones_por_dia[dia] = max_col
    
    # Crear estructura: {dia: {franja: [curso1, curso2, ...]}}
    df_horario = {}
    for dia in DIAS:
        df_horario[dia] = {franja: [] for franja in FRANJAS}
    
    # Ordenar por hora de inicio para procesamiento ordenado
    df_ciclo = df_ciclo.sort_values('hora_inicio')
    
    # PASO CRÍTICO: Asignar cada curso a UNA subcolumna fija
    for _, row in df_ciclo.iterrows():
        info = f"{row['asignatura_nombre']} - {row['profesor_nombre']} - {row['grupo_nombre']} - {row['aula_nombre']}"
        franjas = franjas_ocupadas(row['hora_inicio'], row['hora_fin'])
        dia = row['dia'].strip().upper()
        
        if dia not in DIAS or not franjas:
            continue
        
        # 1. Encontrar la PRIMERA franja del curso
        primera_franja = franjas[0]
        
        # 2. Buscar en qué subcolumna podemos colocar este curso
        # Buscamos la primera posición libre en la primera franja
        subcolumna_asignada = None
        
        # Revisar cada posible subcolumna
        for idx_sub in range(max_colisiones_por_dia[dia]):
            # Verificar si esta subcolumna está libre en TODAS las franjas del curso
            subcolumna_libre = True
            
            for franja in franjas:
                # Asegurar que la lista tenga suficientes elementos
                while len(df_horario[dia][franja]) <= idx_sub:
                    df_horario[dia][franja].append(None)
                
                # Si ya hay algo en esta posición, no está libre
                if df_horario[dia][franja][idx_sub] is not None:
                    subcolumna_libre = False
                    break
            
            # Si encontramos una subcolumna libre en todas las franjas
            if subcolumna_libre:
                subcolumna_asignada = idx_sub
                break
        
        # Si no encontramos subcolumna libre, crear una nueva
        if subcolumna_asignada is None:
            subcolumna_asignada = max(len(df_horario[dia][franjas[0]]) for franja in franjas)
        
        # 3. Asignar el curso a la subcolumna encontrada en TODAS sus franjas
        for franja in franjas:
            # Asegurar que la lista tenga suficiente espacio
            while len(df_horario[dia][franja]) <= subcolumna_asignada:
                df_horario[dia][franja].append(None)
            
            # Colocar el curso en la posición asignada
            df_horario[dia][franja][subcolumna_asignada] = info
    
    # Limpiar None y convertir a strings vacíos
    for dia in DIAS:
        for franja in FRANJAS:
            # Convertir None a string vacío
            df_horario[dia][franja] = [
                c if c is not None else "" 
                for c in df_horario[dia][franja]
            ]
    
    # Detectar franjas activas (que tengan al menos 1 curso)
    franjas_activas = []
    for franja in FRANJAS:
        tiene_contenido = False
        for dia in DIAS:
            if any(c != "" for c in df_horario[dia][franja]):
                tiene_contenido = True
                break
        if tiene_contenido:
            franjas_activas.append(franja)
    
    return df_horario, max_colisiones_por_dia, franjas_activas