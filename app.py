import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Simulación Carbonatación", layout="centered")

# --- TÍTULO PRINCIPAL ---
st.title("SIMULACIÓN: CARBONATACIÓN DEL HORMIGÓN")
st.markdown("""
Modelo de difusión-reacción unidimensional simplificado para visualizar el avance
del frente de carbonatación y el riesgo de corrosión en las armaduras.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros del Modelo")

# 1. Concentración (C)
C_env = st.sidebar.slider("C: Conc. CO₂ Ambiente", 0.5, 2.0, 1.0)
st.sidebar.caption("Mayor C = Ambiente más contaminado")

# 2. Coeficiente de Difusión (D)
D_val = st.sidebar.slider("D: Coef. Difusión (x10⁻⁴)", 0.5, 5.0, 2.0)
st.sidebar.caption("Mayor D = Hormigón más poroso")

# 3. Tasa de Reacción (k)
k_val = st.sidebar.slider("k: Tasa de Reacción", 0.0, 0.2, 0.05, step=0.01)
st.sidebar.caption("Mayor k = Más cemento (Reacciona más y protege mejor)")

# 4. Tiempo
T_years = st.sidebar.slider("Tiempo (Años)", 0, 80, 30)

# Botón para ejecutar
if st.button("▶️ Calcular Estado"):
    
    with st.spinner('Procesando difusión y reacción...'):
        
        # --- PARÁMETROS FÍSICOS ---
        Lx, Ly = 0.5, 0.5  # Columna de 50x50 cm
        Nx, Ny = 50, 50    # Resolución de la malla
        
        # Ajuste de escala para la simulación
        D_sim = D_val * 1e-4 
        
        dx = Lx / (Nx - 1)
        dy = Ly / (Ny - 1)
        
        # Criterio de estabilidad
        dt = 0.2 * min(dx, dy)**2 / D_sim
        
        if T_years == 0:
            Nt = 0
        else:
            Nt = int(T_years / dt)
        
        # Inicialización
        u = np.zeros((Ny, Nx))
        
        # Condiciones de Frontera (Bordes expuestos al CO2)
        u[0, :] = C_env; u[-1, :] = C_env
        u[:, 0] = C_env; u[:, -1] = C_env
        
        u_curr = u.copy()
        
        # --- BUCLE DE SIMULACIÓN ---
        for n in range(Nt):
            # Laplaciano (Difusión)
            laplacian = (
                (u_curr[0:-2, 1:-1] - 2*u_curr[1:-1, 1:-1] + u_curr[2:, 1:-1]) / dy**2 +
                (u_curr[1:-1, 0:-2] - 2*u_curr[1:-1, 1:-1] + u_curr[1:-1, 2:]) / dx**2
            )
            
            # Ecuación completa: Difusión - Reacción
            u_curr[1:-1, 1:-1] += dt * (D_sim * laplacian - k_val * u_curr[1:-1, 1:-1])
            
            # Reforzar bordes
            u_curr[0, :] = C_env; u_curr[-1, :] = C_env
            u_curr[:, 0] = C_env; u_curr[:, -1] = C_env

        # --- GRAFICAR EL RESULTADO ---
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # Mapa de calor
        im = ax.imshow(u_curr, extent=[0, Lx, 0, Ly], origin="lower", cmap="RdYlBu_r", vmin=0, vmax=C_env)
        cbar = plt.colorbar(im)
        cbar.set_label("Concentración de CO₂")
        
        # Línea de frente de carbonatación (Umbral visual en 0.4)
        if np.max(u_curr) > 0.4:
            ax.contour(u_curr, levels=[0.4], extent=[0, Lx, 0, Ly], origin="lower", colors='black', linewidths=2)
        
        # --- DIBUJAR LAS 4 ARMADURAS ---
        recubrimiento = 0.05 # 5 cm
        
        x_rebar = [recubrimiento, Lx-recubrimiento, recubrimiento, Lx-recubrimiento]
        y_rebar = [recubrimiento, recubrimiento, Ly-recubrimiento, Ly-recubrimiento]
        
        ax.scatter(x_rebar, y_rebar, c='black', s=150, label="Armadura", edgecolors='white', zorder=10)
        
        ax.legend(loc="upper center", framealpha=0.9)
        ax.set_title(f"Avance tras {T_years} años\n(k={k_val}, D={D_val})")
        ax.set_xlabel("Ancho (m)")
        ax.set_ylabel("Alto (m)")
        
        st.pyplot(fig)
        
        # --- DIAGNÓSTICO DE SEGURIDAD ---
        idx_rebar = int(recubrimiento / dx)
        conc_en_acero = u_curr[idx_rebar, idx_rebar]
        
        # AQUÍ ESTÁ EL CAMBIO DE MENSAJE
        if conc_en_acero > 0.4:
            st.error(f"⚠️ ¡PELIGRO! La armadura corre peligro de corrosión.")
        else:
            st.success(f"✅ ESTRUCTURA SEGURA. La armadura sigue protegida.")

else:
    st.info("Ajusta los parámetros C, D y k en el menú lateral y presiona 'Calcular'.")