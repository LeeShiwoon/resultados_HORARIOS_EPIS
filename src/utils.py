from datetime import datetime, timedelta

# Generar franjas dinámicas desde min_hora hasta max_hora
def generar_franjas(min_hora="08:00", max_hora="22:15", duracion_min=45):
    franjas = []
    inicio = datetime.strptime(min_hora, "%H:%M")
    fin = datetime.strptime(max_hora, "%H:%M")

    while inicio < fin:
        fin_franja = inicio + timedelta(minutes=duracion_min)
        franjas.append(f"{inicio.strftime('%H:%M')} - {fin_franja.strftime('%H:%M')}")
        inicio = fin_franja
    return franjas

FRANJAS = generar_franjas()

def str_a_hora(hora_str):
    return datetime.strptime(hora_str, "%H:%M")

def franjas_ocupadas(hora_inicio, hora_fin):
    inicio = str_a_hora(hora_inicio)
    fin = str_a_hora(hora_fin)
    franjas = []
    for franja in FRANJAS:
        f_inicio, f_fin = franja.split(" - ")
        f_inicio_dt = str_a_hora(f_inicio)
        f_fin_dt = str_a_hora(f_fin)
        if (inicio < f_fin_dt) and (fin > f_inicio_dt):
            franjas.append(franja)
    return franjas
