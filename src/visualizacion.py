"""
Módulo de visualización de horarios con interfaz gráfica Tkinter
"""
import tkinter as tk
from tkinter import messagebox

from anyio import Path
from exportar import (generar_color_pastel, exportar_a_pdf, exportar_todos_pdf,
                     exportar_horario_excel, exportar_todos_excel)
from horario import DIAS


def mostrar_horarios_navegables(horarios_dict, max_colisiones_dict, franjas_activas_dict):
    """Muestra horarios con subcolunas dinámicas agrupadas bajo un solo encabezado."""
    ciclos = sorted(list(horarios_dict.keys()))
    idx_actual = [0]

    root = tk.Tk()
    root.title("Visualizador de Horarios Académicos")
    root.state('zoomed')
    
    # Frame superior
    top_frame = tk.Frame(root, bg='#2F5496', height=50)
    top_frame.pack(fill=tk.X, side=tk.TOP)
    top_frame.pack_propagate(False)
    
    info_label = tk.Label(
        top_frame,
        text="",
        font=("Arial", 14, "bold"),
        bg='#2F5496',
        fg='white'
    )
    info_label.pack(expand=True)
    
    # Frame para la tabla
    table_frame = tk.Frame(root, bg='white')
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(table_frame, bg='white')
    scrollbar_v = tk.Scrollbar(table_frame, orient='vertical', command=canvas.yview)
    scrollbar_h = tk.Scrollbar(table_frame, orient='horizontal', command=canvas.xview)
    
    scrollable_frame = tk.Frame(canvas, bg='white')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    
    scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def limpiar_tabla():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
    
    def dibujar_horario():
        limpiar_tabla()
        
        ciclo = ciclos[idx_actual[0]]
        df_horario = horarios_dict[ciclo]
        max_colisiones = max_colisiones_dict[ciclo]
        franjas_activas = franjas_activas_dict[ciclo]
        
        info_label.config(
            text=f"CICLO {ciclo} - Horario Académico ({idx_actual[0]+1}/{len(ciclos)})"
        )
        
        colores_asignaturas = {}
        
        style_config = {
            'borderwidth': 1,
            'relief': 'solid',
            'padx': 5,
            'pady': 5
        }
        
        # Columna 0: Horarios
        col_actual = 0
        
        header_cell = tk.Label(
            scrollable_frame,
            text="HORARIO",
            bg='#2F5496',
            fg='white',
            font=('Arial', 10, 'bold'),
            **style_config
        )
        header_cell.grid(row=0, column=col_actual, sticky='nsew')
        scrollable_frame.columnconfigure(col_actual, minsize=120)
        col_actual += 1
        
        # Encabezados de días
        for dia in DIAS:
            num_subcols = max_colisiones[dia]
            
            header_cell = tk.Label(
                scrollable_frame,
                text=dia,
                bg='#2F5496',
                fg='white',
                font=('Arial', 10, 'bold'),
                **style_config
            )
            header_cell.grid(row=0, column=col_actual, columnspan=num_subcols, sticky='nsew')
            
            for sub_idx in range(num_subcols):
                scrollable_frame.columnconfigure(col_actual + sub_idx, minsize=300, weight=1)
            
            col_actual += num_subcols
        
        # Filas de datos
        for i, franja in enumerate(franjas_activas):
            time_cell = tk.Label(
                scrollable_frame,
                text=franja,
                bg='#D0CECE',
                font=('Arial', 8, 'bold'),
                **style_config
            )
            time_cell.grid(row=i+1, column=0, sticky='nsew')
            scrollable_frame.rowconfigure(i+1, minsize=70)
            
            col_actual = 1
            for dia in DIAS:
                cursos = df_horario[dia][franja]
                num_subcols = max_colisiones[dia]
                
                while len(cursos) < num_subcols:
                    cursos.append("")
                
                for idx_sub in range(num_subcols):
                    valor = cursos[idx_sub] if idx_sub < len(cursos) else ""
                    
                    if valor and str(valor).strip() != "":
                        asignatura = str(valor).split(' - ')[0].strip()
                        
                        if asignatura not in colores_asignaturas:
                            colores_asignaturas[asignatura] = f"#{generar_color_pastel(asignatura)}"
                        
                        bg_color = colores_asignaturas[asignatura]
                    else:
                        bg_color = 'white'
                    
                    data_cell = tk.Label(
                        scrollable_frame,
                        text=valor,
                        bg=bg_color,
                        font=('Arial', 7),
                        wraplength=280,
                        justify='left',
                        **style_config
                    )
                    data_cell.grid(row=i+1, column=col_actual, sticky='nsew')
                    col_actual += 1
    
    def siguiente():
        if idx_actual[0] < len(ciclos) - 1:
            idx_actual[0] += 1
            dibujar_horario()
    
    def anterior():
        if idx_actual[0] > 0:
            idx_actual[0] -= 1
            dibujar_horario()
    
    def exportar_pdf_actual():
        ciclo = ciclos[idx_actual[0]]
        file_path = exportar_a_pdf(horarios_dict[ciclo], max_colisiones_dict[ciclo], 
                                   franjas_activas_dict[ciclo], ciclo)
        messagebox.showinfo("✓ PDF Exportado", f"PDF generado:\n\n{file_path}")
    
    def exportar_pdf_todos():
        file_path = exportar_todos_pdf(horarios_dict, max_colisiones_dict, franjas_activas_dict)
        messagebox.showinfo("✓ PDFs Exportados", f"PDF completo generado:\n\n{file_path}")
    
    def exportar_excel_actual():
        ciclo = ciclos[idx_actual[0]]
        file_path = exportar_horario_excel(horarios_dict[ciclo], max_colisiones_dict[ciclo],
                                          franjas_activas_dict[ciclo], ciclo)
        messagebox.showinfo("✓ Excel Exportado", f"Excel generado:\n\n{file_path}")
    
    def exportar_excel_todos():
        archivos = exportar_todos_excel(horarios_dict, max_colisiones_dict, franjas_activas_dict)
        mensaje = f"Se generaron {len(archivos)} archivos Excel:\n\n"
        mensaje += "\n".join([f"• {Path(f).name}" for f in archivos[:3]])
        if len(archivos) > 3:
            mensaje += f"\n... y {len(archivos)-3} más"
        messagebox.showinfo("✓ Excels Exportados", mensaje)
    
    def cerrar_ventana():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", cerrar_ventana)
    
    # Frame de botones
    btn_frame = tk.Frame(root, bg='#F0F0F0', height=70)
    btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
    btn_frame.pack_propagate(False)
    
    btn_container = tk.Frame(btn_frame, bg='#F0F0F0')
    btn_container.pack(expand=True)
    
    # Navegación
    btn_anterior = tk.Button(
        btn_container, text="◄ Anterior", command=anterior,
        font=("Arial", 10, "bold"), bg='#4472C4', fg='white',
        width=11, height=2, cursor='hand2'
    )
    btn_anterior.pack(side=tk.LEFT, padx=5)
    
    btn_siguiente = tk.Button(
        btn_container, text="Siguiente ►", command=siguiente,
        font=("Arial", 10, "bold"), bg='#4472C4', fg='white',
        width=11, height=2, cursor='hand2'
    )
    btn_siguiente.pack(side=tk.LEFT, padx=5)
    
    tk.Frame(btn_container, bg='#CCCCCC', width=2, height=40).pack(side=tk.LEFT, padx=10)
    
    # Exportar PDFs
    btn_pdf_actual = tk.Button(
        btn_container, text="📄 PDF", command=exportar_pdf_actual,
        font=("Arial", 9, "bold"), bg='#E67E22', fg='white',
        width=10, height=2, cursor='hand2'
    )
    btn_pdf_actual.pack(side=tk.LEFT, padx=5)
    
    btn_pdf_todos = tk.Button(
        btn_container, text="📚 PDFs", command=exportar_pdf_todos,
        font=("Arial", 9, "bold"), bg='#D35400', fg='white',
        width=10, height=2, cursor='hand2'
    )
    btn_pdf_todos.pack(side=tk.LEFT, padx=5)
    
    tk.Frame(btn_container, bg='#CCCCCC', width=2, height=40).pack(side=tk.LEFT, padx=10)
    
    # Exportar Excels
    btn_excel_actual = tk.Button(
        btn_container, text="📊 Excel", command=exportar_excel_actual,
        font=("Arial", 9, "bold"), bg='#27AE60', fg='white',
        width=10, height=2, cursor='hand2'
    )
    btn_excel_actual.pack(side=tk.LEFT, padx=5)
    
    btn_excel_todos = tk.Button(
        btn_container, text="📑 Excels", command=exportar_excel_todos,
        font=("Arial", 9, "bold"), bg='#229954', fg='white',
        width=10, height=2, cursor='hand2'
    )
    btn_excel_todos.pack(side=tk.LEFT, padx=5)
    
    tk.Frame(btn_container, bg='#CCCCCC', width=2, height=40).pack(side=tk.LEFT, padx=10)
    
    # Cerrar
    btn_cerrar = tk.Button(
        btn_container, text="✖ Cerrar", command=cerrar_ventana,
        font=("Arial", 9, "bold"), bg='#E74C3C', fg='white',
        width=9, height=2, cursor='hand2'
    )
    btn_cerrar.pack(side=tk.LEFT, padx=5)
    
    dibujar_horario()
    root.mainloop()
