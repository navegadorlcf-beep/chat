
import streamlit as st
import sqlite3
from datetime import datetime

# =============================
# CONFIGURAÇÃO DA PÁGINA
# =============================
st.set_page_config(
    page_title="Chat Seguro 💬",
    page_icon="💬",
    layout="centered"
)

# =============================
# BANCO DE DADOS
# =============================
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remetente TEXT NOT NULL,
    destinatario TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    data TEXT NOT NULL
)
""")
conn.commit()

# =============================
# SESSÃO
# =============================
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# =============================
# LOGIN (BLINDADO)
# =============================
if st.session_state.usuario == "":
    st.title("💬 Entrar no Chat")

    # 🔒 Campo invisível anti-autofill
    st.text_input(
        "",
        value="",
        label_visibility="collapsed",
        key="anti_autofill_hidden"
    )

    apelido = st.text_input(
        "seu nome?",
        key="campo_apelido_chat"
    )

    if st.button("Entrar no chat"):
        if apelido.strip():
            st.session_state.usuario = apelido.strip()
            st.rerun()
        else:
            st.warning("Digite algo para continuar.")

    st.stop()

usuario = st.session_state.usuario

# =============================
# INTERFACE PRINCIPAL
# =============================
st.title("💬 Chat Privado")
st.caption(f"seu nome: **{usuario}**")

# 🔒 Outro campo anti-autofill
st.text_input(
    "",
    value="",
    label_visibility="collapsed",
    key="anti_autofill_hidden_2"
)

destinatario = st.text_input(
    "Conversar com quem?",
    key="campo_destinatario_chat"
)

# =============================
# ENVIO DE MENSAGEM
# =============================
with st.form("form_envio", clear_on_submit=True):
    mensagem = st.text_area(
        "Escreva sua mensagem",
        key="campo_mensagem_chat"
    )
    enviar = st.form_submit_button("Enviar")

    if enviar:
        if destinatario.strip() == "" or mensagem.strip() == "":
            st.warning("Preencha o destinatário e a mensagem.")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            cursor.execute("""
                INSERT INTO mensagens (remetente, destinatario, mensagem, data)
                VALUES (?, ?, ?, ?)
            """, (usuario, destinatario.strip(), mensagem.strip(), data))
            conn.commit()
            st.success("Mensagem enviada!")

# =============================
# EXIBIR CONVERSA
# =============================
if destinatario.strip():
    st.divider()
    st.subheader(f"📨 Conversa com {destinatario}")

    cursor.execute("""
        SELECT id, remetente, mensagem, data
        FROM mensagens
        WHERE (remetente = ? AND destinatario = ?)
           OR (remetente = ? AND destinatario = ?)
        ORDER BY id ASC
    """, (usuario, destinatario, destinatario, usuario))

    mensagens = cursor.fetchall()

    for msg_id, remetente, texto, data in mensagens:
        icone = "🟦" if remetente == usuario else "🟩"

        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(
                f"""
                {icone} **{remetente}**  
                {texto}  
                <small>{data}</small>
                """,
                unsafe_allow_html=True
            )
        with col2:
            if remetente == usuario:
                if st.button("🗑️", key=f"del_{msg_id}"):
                    cursor.execute(
                        "DELETE FROM mensagens WHERE id = ?",
                        (msg_id,)
                    )
                    conn.commit()
                    st.rerun()

# =============================
# SAIR
# =============================
st.divider()
if st.button("🚪 Sair do chat"):
    st.session_state.usuario = ""
    st.rerun()