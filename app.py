import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Simulación Carbonatación", layout="centered")

# Título y explicación simple
st.title("🛡️ Carbonatación del Hormigón")
st.write("""
Mueve los controles deslizantes para simular cómo entra el CO₂ en el hormigón
y cuándo llega a las armaduras de acero.
""")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("Parámetros")

# Sliders
C_env = st.sidebar.slider("Concentración CO₂ (Ambiente)", 0.5, 2.0, 1.0)
st.sidebar.caption("Más alto = Ambiente más contaminado")

D_val = st.sidebar.slider("Permeabilidad (D)", 0.5, 5.0, 1.0)
st.sidebar.caption("Más alto = Hormigón más poroso (mala calidad)")

T_years = st.sidebar.slider("Años a simular", 10, 80, 50)

# Botón mágico
if st.button("▶️ ¡Ejecutar Simulación!"):
    
    with st.spinner('Calculando la difusión del CO₂...'):
        
        # --- CÁLCULOS MATEMÁTICOS (Tu modelo) ---
        Lx, Ly = 0.5, 0.5  # 50x50 cm
        Nx, Ny = 50, 50    # Malla de puntos
        
        # Ajuste de D para la escala
        D_sim = D_val * 1e-4 
        k = 0.05 # Tasa de reacción fija para simplificar
        
        dx = Lx / (Nx - 1)
        dy = Ly / (Ny - 1)
        # Paso de tiempo estable
        dt = 0.2 * min(dx, dy)**2 / D_sim
        Nt = int(T_years / dt)
        
        # Matriz inicial (todo en 0)
        u = np.zeros((Ny, Nx))
        
        # Bordes con CO2
        u[0, :] = C_env; u[-1, :] = C_env
        u[:, 0] = C_env; u[:, -1] = C_env
        
        u_curr = u.copy()
        
        # Bucle rápido (solo calculamos el estado final para no trabar el celular)
        for n in range(Nt):
            laplacian = (
                (u_curr[0:-2, 1:-1] - 2*u_curr[1:-1, 1:-1] + u_curr[2:, 1:-1]) / dy**2 +
                (u_curr[1:-1, 0:-2] - 2*u_curr[1:-1, 1:-1] + u_curr[1:-1, 2:]) / dx**2
            )
            u_curr[1:-1, 1:-1] += dt * (D_sim * laplacian - k * u_curr[1:-1, 1:-1])
            
            # Reforzar bordes
            u_curr[0, :] = C_env; u_curr[-1, :] = C_env
            u_curr[:, 0] = C_env; u_curr[:, -1] = C_env

        # --- GRAFICAR EL RESULTADO ---
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # Mapa de colores (Azul=Sano, Rojo=Carbonatado)
        im = ax.imshow(u_curr, extent=[0, Lx, 0, Ly], origin="lower", cmap="RdYlBu_r", vmin=0, vmax=C_env)
        plt.colorbar(im, label="Concentración CO₂")
        
        # Línea de peligro (Frente de carbonatación)
        # Si la concentración > 0.4, dibujamos la línea
        if np.max(u_curr) > 0.4:
            ax.contour(u_curr, levels=[0.4], extent=[0, Lx, 0, Ly], origin="lower", colors='black', linewidths=2)
        
        # Dibujar las varillas de acero (Puntos negros)
        recubrimiento = 0.05 # 5 cm
        ax.scatter([recubrimiento, Lx-recubrimiento], [recubrimiento, recubrimiento], c='black', s=150, label="Acero", edgecolors='white')
        ax.legend(loc="upper center")
        
        ax.set_title(f"Estado del Hormigón tras {T_years} años")
        ax.set_xlabel("Ancho (m)")
        ax.set_ylabel("Alto (m)")
        
        st.pyplot(fig)
        
        # Mensaje final
        if u_curr[5, 5] > 0.4: # Chequeo rápido cerca de la esquina
            st.error("⚠️ ¡ALERTA! El CO₂ ha llegado al nivel de las armaduras. Riesgo de corrosión.")
        else:
            st.success("✅ El acero aún está protegido.")

else:
    st.info("Ajusta los parámetros a la izquierda y presiona el botón.")