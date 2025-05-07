import streamlit as st
from app.agent import run_supabase_agent

st.set_page_config(page_title="Supabase AI Agent", layout="centered")

st.title("🧠 Supabase AI Agent")
st.markdown(
    "Execute queries diretamente usando a inteligência do seu agente CrewAI + Supabase!"
)

query = st.text_area("Escreva sua consulta SQL Supabase aqui:", height=150)

if st.button("Executar"):
    if query.strip() == "":
        st.warning("Por favor, insira uma query válida.")
    else:
        with st.spinner("Executando o agente..."):
            try:
                result = run_supabase_agent(query)
                st.success("✅ Operação concluída com sucesso!")
                st.json(result)
            except Exception as e:
                st.error(f"❌ Erro ao executar o agente:\n\n{e}")
