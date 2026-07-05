import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD
# ==========================================
st.set_page_config(
    page_title="Dante's Collection",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para la paleta de colores: Negro, Dorado y Blanco
st.markdown("""
    <style>
    .stApp {
        background-color: #0d0d0d;
        color: #ffffff;
    }
    h1, h2, h3, .gold-text {
        color: #f39c12 !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        text-align: center;
    }
    .card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #f39c12;
        margin-bottom: 15px;
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #222222 !important;
        color: #ffffff !important;
        border-color: #f39c12 !important;
    }
    .stButton>button {
        background-color: #f39c12 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 5px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e67e22 !important;
        color: #000000 !important;
        box-shadow: 0 0 10px #f39c12;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111111;
        padding: 5px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: #1a1a1a;
        border-radius: 5px;
        color: #cccccc;
        font-size: 14px;
        border: 1px solid #333333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f39c12 !important;
        color: #000000 !important;
        font-weight: bold;
        border: 1px solid #f39c12 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>👑 DANTE'S COLLECTION 👑</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888; font-style: italic;'>Taller de Camisas Exclusive</p>", unsafe_allow_html=True)

# ==========================================
# 2. SISTEMA DE SEGURIDAD (PIN)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if not st.session_state.authenticated:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #f39c12; text-align: center;'>🔒 Acceso Privado</h3>", unsafe_allow_html=True)
    pin_input = st.text_input("Ingrese su PIN de Acceso:", type="password")
    col1, col2 = st.columns(2)
    with col1:
        vendedor_login = st.selectbox("¿Quién ingresa?", ["Daniel", "Slendy"])
    with col2:
        st.write("")
        st.write("")
        btn_login = st.button("Ingresar")
    if btn_login:
        if pin_input in ["2026", "1234"]:
            st.session_state.authenticated = True
            st.session_state.usuario = vendedor_login
            st.success(f"¡Bienvenido, {vendedor_login}!")
            st.rerun()
        else:
            st.error("❌ PIN Incorrecto.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown(f"<p style='text-align: right; color: #f39c12; font-weight: bold;'>👤 Sesión: {st.session_state.usuario}</p>", unsafe_allow_html=True)

# ==========================================
# 3. CONEXIÓN A GOOGLE SHEETS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def cargar_inventario():
    try:
        df = conn.read(worksheet="Inventario", ttl=5)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        # Inicialización de 24 variantes por defecto si no existen
        modelos = ["Oversized", "Algodón Licrado"]
        colores = ["Negro", "Blanco", "Beige"]
        tallas = ["S", "M", "L", "XL"]
        rows = []
        idx = 1
        for model in modelos:
            for color in colores:
                for size in tallas:
                    rows.append({
                        "id": idx, "name": f"Camisa {model} {color} {size}",
                        "color": color, "size": size,
                        "stock_liso": 50, "stock_apartado": 0, "stock_estampado": 0
                    })
                    idx += 1
        return pd.DataFrame(rows)

@st.cache_data(ttl=5)
def cargar_pedidos():
    try:
        df = conn.read(worksheet="Pedidos", ttl=5)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=[
            "id", "customerName", "model", "color", "size", 
            "quantity", "printDesign", "status", "createdAt", "notes", "vendedor"
        ])

df_inv = cargar_inventario()
df_ped = cargar_pedidos()

# Ajustar formatos numéricos
df_inv["id"] = df_inv["id"].astype(int)
df_inv["stock_liso"] = df_inv["stock_liso"].astype(int)
df_inv["stock_apartado"] = df_inv["stock_apartado"].astype(int)
df_inv["stock_estampado"] = df_inv["stock_estampado"].astype(int)
if not df_ped.empty:
    df_ped["id"] = df_ped["id"].astype(int)
    df_ped["quantity"] = df_ped["quantity"].astype(int)

# ==========================================
# 4. TABS
# ==========================================
tab_nuevo, tab_gestion, tab_inventario, tab_reportes = st.tabs([
    "🛒 Nuevo Pedido", "📦 Gestión", "🗃️ Inventario", "📊 Reportes"
])

# -- NUEVO PEDIDO --
with tab_nuevo:
    st.markdown("<h3 style='color: #f39c12;'>📝 Registrar Pedido</h3>", unsafe_allow_html=True)
    with st.form("form_pedido"):
        customer_name = st.text_input("Cliente:")
        model_select = st.selectbox("Modelo:", ["Oversized", "Algodón Licrado"])
        color_select = st.selectbox("Color:", sorted(df_inv["color"].unique()))
        size_select = st.selectbox("Talla:", ["S", "M", "L", "XL"])
        
        match_inv = df_inv[(df_inv["name"].str.contains(model_select)) & (df_inv["color"] == color_select) & (df_inv["size"] == size_select)]
        stock_disponible = int(match_inv.iloc[0]["stock_liso"]) if not match_inv.empty else 0
        variant_id = int(match_inv.iloc[0]["id"]) if not match_inv.empty else None
        
        st.info(f"💡 Stock liso disponible: {stock_disponible} unidades.")
        quantity = st.number_input("Cantidad:", min_value=1, value=1, step=1)
        print_design = st.text_input("Diseño del Estampado:")
        notes = st.text_area("Notas:")
        vendedor_pedido = st.selectbox("Vendedor:", ["Daniel", "Slendy"])
        
        btn_registrar = st.form_submit_button("Confirmar Pedido 🚀")
        if btn_registrar:
            if not customer_name.strip():
                st.error("Ingrese el nombre del cliente.")
            elif quantity > stock_disponible:
                st.error("Stock liso insuficiente.")
            else:
                # Restar stock liso, sumar apartado
                df_inv.loc[df_inv["id"] == variant_id, "stock_liso"] -= quantity
                df_inv.loc[df_inv["id"] == variant_id, "stock_apartado"] += quantity
                
                new_id = 1 if df_ped.empty else int(df_ped["id"].max()) + 1
                new_order = pd.DataFrame([{
                    "id": new_id, "customerName": customer_name.strip(), "model": model_select,
                    "color": color_select, "size": size_select, "quantity": int(quantity),
                    "printDesign": print_design if print_design.strip() else "Liso",
                    "status": "Pendiente", "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": notes, "vendedor": vendedor_pedido
                }])
                df_ped = pd.concat([df_ped, new_order], ignore_index=True)
                
                conn.update(worksheet="Inventario", data=df_inv)
                conn.update(worksheet="Pedidos", data=df_ped)
                st.success("¡Pedido registrado exitosamente!")
                st.rerun()

# -- GESTIÓN --
with tab_gestion:
    st.markdown("<h3 style='color: #f39c12;'>📦 Gestión de Pedidos</h3>", unsafe_allow_html=True)
    if df_ped.empty:
        st.info("No hay pedidos registrados.")
    else:
        for idx, row in df_ped.iterrows():
            with st.container():
                st.markdown(f"<div class='card'><b>Pedido #{row['id']} - {row['customerName']}</b><br>Cantidad: {row['quantity']} | Vendedor: {row['vendedor']} | Estado: {row['status']}</div>", unsafe_allow_html=True)
                if row["status"] == "Pendiente":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Completar #{row['id']}", key=f"c_{row['id']}"):
                            # Restar apartado, sumar estampado
                            match_v = df_inv[(df_inv["name"].str.contains(row['model'])) & (df_inv["color"] == row['color']) & (df_inv["size"] == row['size'])]
                            if not match_v.empty:
                                v_id = match_v.iloc[0]["id"]
                                df_inv.loc[df_inv["id"] == v_id, "stock_apartado"] -= int(row['quantity'])
                                df_inv.loc[df_inv["id"] == v_id, "stock_estampado"] += int(row['quantity'])
                                df_ped.loc[df_ped["id"] == row["id"], "status"] = "Finalizado"
                                conn.update(worksheet="Inventario", data=df_inv)
                                conn.update(worksheet="Pedidos", data=df_ped)
                                st.success("Pedido completado.")
                                st.rerun()
                    with col2:
                        if st.button(f"Cancelar #{row['id']}", key=f"x_{row['id']}"):
                            # Devolver apartado a liso
                            match_v = df_inv[(df_inv["name"].str.contains(row['model'])) & (df_inv["color"] == row['color']) & (df_inv["size"] == row['size'])]
                            if not match_v.empty:
                                v_id = match_v.iloc[0]["id"]
                                df_inv.loc[df_inv["id"] == v_id, "stock_apartado"] -= int(row['quantity'])
                                df_inv.loc[df_inv["id"] == v_id, "stock_liso"] += int(row['quantity'])
                                df_ped.loc[df_ped["id"] == row["id"], "status"] = "Cancelado"
                                conn.update(worksheet="Inventario", data=df_inv)
                                conn.update(worksheet="Pedidos", data=df_ped)
                                st.success("Pedido cancelado.")
                                st.rerun()

# -- INVENTARIO --
with tab_inventario:
    st.markdown("<h3 style='color: #f39c12;'>🗃️ Inventario</h3>", unsafe_allow_html=True)
    st.dataframe(df_inv[["id", "name", "stock_liso", "stock_apartado", "stock_estampado"]], use_container_width=True, hide_index=True)

# -- REPORTES --
with tab_reportes:
    st.markdown("<h3 style='color: #f39c12;'>📊 Reportes</h3>", unsafe_allow_html=True)
    if not df_ped.empty:
        df_ventas = df_ped[df_ped["status"] != "Cancelado"]
        if not df_ventas.empty:
            sales_by_vendedor = df_ventas.groupby("vendedor")["quantity"].sum().reset_index()
            fig = px.bar(sales_by_vendedor, x="vendedor", y="quantity", color="vendedor", template="plotly_dark", color_discrete_sequence=["#f39c12"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin ventas completadas o pendientes aún.")
    else:
        st.info("Registra pedidos para ver los análisis gráficos.")