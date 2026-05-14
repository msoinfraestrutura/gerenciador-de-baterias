import streamlit as st
from services.api_client import (
    run_load_data, 
    run_feature_engineering, 
    run_training_data,
    run_full_pipeline
)


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Motor de Alocações')
    
    st.write('---')

    #parâmetros do modelo
    with st.expander('⚙️ Parâmetros', expanded=False):
        st.markdown('### 💲Investimento')
        investimento = st.number_input(
            label='Investimento',
            min_value=0.0,
            value=93_634_178.16,
            step=1_000_000.0,
            label_visibility='collapsed' 
        )

        st.markdown('### 🔋Baterias')
        
        st.markdown('**Selada VRLA 12V**')
        col1, col2 = st.columns(2)
        with col1:
            selada_vrla_custo = st.number_input('Custo Unitário', value=9575.12, key='input_custo_selada')
        with col2:
            selada_vrla_capacidade = st.number_input('Capacidade (Ah)', value=200, key='input_capacidade_selada')
        
        st.markdown('**Ventilada 2V**')
        col1, col2 = st.columns(2)
        with col1:
            ventilada_custo = st.number_input('Custo Unitário', value=145826.37, key='input_custo_ventilada') 
        with col2:
            ventilada_capacidade = st.number_input('Capacidade (Ah)', value=2000, key='input_capacidade_ventilada')

        st.markdown('**Lítio 48V**')
        col1, col2 = st.columns(2)
        with col1:
            litio_custo = st.number_input('Custo Unitário', value=14842.56, key='input_custo_litio')
        with col2:
            litio_capacidade = st.number_input('Capacidade (Ah)', value=100, key='input_capacidade_litio')

    #preparação do payload para as funções que o utilizam
    payload = {
        'investimento': investimento,
        'baterias': {
            'SELADA (VRLA) 12V': {
                'tipo_bateria': 'SELADA (VRLA)',
                'tensao': 12,
                'capacidade': selada_vrla_capacidade,
                'custo': selada_vrla_custo
            },
            'VENTILADA 2V': {
                'tipo_bateria': 'VENTILADA',
                'tensao': 2,
                'capacidade': ventilada_capacidade,
                'custo': ventilada_custo
            },
            'LITIO 48V': {
                'tipo_bateria': 'LITIO',
                'tensao': 48,
                'capacidade': litio_capacidade,
                'custo': litio_custo
            }
        }
    }

    #pipeline completo
    st.subheader('Pipeline')
    st.info('Executa todas as etapas do pipeline.')
    
    if st.button('Executar', type='primary', width='stretch'):
        with st.status('Executando pipeline completo...', expanded=True) as status:
            try:
                st.write('Processando todas as etapas na API...')
                result = run_full_pipeline(config=payload)
                
                status.update(label='Pipeline finalizado com sucesso!', state='complete', expanded=False)
                st.success('Otimização concluída. Os resultados já estão disponíveis para consulta.')
                
                with st.expander('Ver detalhes do retorno'):
                    st.json(result)
            except Exception as e:
                status.update(label='Falha no Pipeline', state='error')
                st.error(f'Erro durante a execução: {e}')

    st.write('---')

    #pipeline parcial
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('① Extração de Dados')
        if st.button('Executar', key='btn_ext', width='stretch'):
            with st.spinner('Extraindo...'):
                try:
                    res = run_load_data()
                    st.success('Extração de dados concluída')
                except Exception as e:
                    st.error(f'Erro: {e}')

    with col2:
        st.subheader('② Engenharia de Features')
        if st.button('Executar', key='btn_feat', width='stretch'):
            with st.spinner('Transformando...'):
                try:
                    res = run_feature_engineering()
                    st.success('Feature engineering concluído')
                except Exception as e:
                    st.error(f'Erro: {e}')

    with col3:
        st.subheader('③ Motor de Alocações')
        if st.button('Executar', key='btn_opt', width='stretch'):
            with st.spinner('Otimizando...'):
                try:
                    res = run_training_data(config=payload)
                    st.success('Alocações concluídas')
                    with st.expander('Ver JSON'):
                        st.json(res)
                except Exception as e:
                    st.error(f'Erro: {e}')