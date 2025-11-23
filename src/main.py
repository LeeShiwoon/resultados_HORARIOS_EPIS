import pandas as pd
from horario import crear_horario_ciclo
from visualizacion import mostrar_horarios_navegables

# Leer CSV
df = pd.read_csv("data/horario_final.csv")

# Ciclos que quieres mostrar
ciclos = [1, 2, 4, 6, 8, 10]

# Generar horarios
horarios_dict = {}
max_colisiones_dict = {}
franjas_activas_dict = {}

for ciclo in ciclos:
    df_horario, max_colisiones, franjas_activas = crear_horario_ciclo(df, ciclo)
    horarios_dict[ciclo] = df_horario
    max_colisiones_dict[ciclo] = max_colisiones
    franjas_activas_dict[ciclo] = franjas_activas

print("=" * 60)
print("VISUALIZADOR DE HORARIOS ACADÉMICOS")
print("=" * 60)
print(f"✓ {len(ciclos)} horarios cargados correctamente")
print("\nAbriendo interfaz gráfica...")

# Mostrar en ventana interactiva
mostrar_horarios_navegables(horarios_dict, max_colisiones_dict, franjas_activas_dict)
print("\n✓ Ventana cerrada. Programa finalizado.")