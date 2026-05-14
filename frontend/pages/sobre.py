import streamlit as st
import pandas as pd


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Sobre')

    st.markdown('''
        <div style='text-align: justify;'>
            <p>
                O modelo greedy é uma técnica de otimização que resolve problemas por meio da seleção iterativa de escolhas localmente ótimas. Em cada iteração, seleciona-se o componente que proporciona o maior ganho marginal imediato, buscando uma solução local que se espera conduzir a uma solução globalmente ótima.
            </p>
            <p>
                No contexto do otimizador de baterias, o modelo é empregado para a alocação de bancos de baterias em um cenário de investimento limitado. O objetivo é determinar a distribuição mais eficiente do investimento entre as estações da planta, priorizando o melhor custo-benefício.
            </p>
        </div>
    ''', unsafe_allow_html=True)
    st.subheader('Dados')
    st.markdown('''
        <div style='text-align: justify;'>
            <p>
                O algoritmo identifica a melhor alocação possível considerando três variáveis: <strong>pontuação</strong>, <strong>ganho marginal</strong> e <strong>custo</strong>.
                O modelo é aplicado para estações com pontuação dentro do terceiro quartil dos dados, classificados como de alta prioridade.
                Com base na pontuação de hierarquia da estação, um tipo de bateria (<strong>Selada (VRLA) 12V</strong>, <strong>Ventilada 2V</strong>, <strong>Lítio 48V</strong>) é atribuído, com seu custo e capacidade associado.
            </p>
        </div>
    ''', unsafe_allow_html=True)
    st.subheader('Função')
    st.markdown('''
        <div style='text-align: justify;'>
            <p>
                Para cada estação com indisponibilidade, um índice de prioridade (ratio) é atribuído pela função abaixo:
            </p>
        </div>
    ''', unsafe_allow_html=True)
    st.latex(r'''
        \Large \text{ratio} \text{ } = \text{ } \frac{\text{pontuação} \times \text{ganho marginal}}{\text{custo}}
    ''')
    st.markdown('''
        <div style='text-align: justify;'>
            <p>Onde:</p>
            <ul style='list-style-type: none; padding-left: 0;'>
                <li><strong>pontuação</strong>: atua como peso, dando mais importância a estações de maior criticidade. O pontuação é a média ponderada de 7 variáveis: autonomia, volume de dados, hierarquia da estação, tempo médio de reparo, idade das baterias, faturamento da estação e tipo de cliente.</li>
                <li><strong>ganho marginal</strong>: redução da autonomia pendente (indisponibilidade em horas) que seria alcançada se um recurso fosse alocado na estação. O cálculo leva em conta a capacidade do banco de bateria e a carga da estação para determinar a autonomia que o banco de bateria adicionaria em cada ocorrência.</li>
                <li><strong>custo</strong>: custo do banco de bateria atribuído.</li>
            </ul>
            <p>
                O algoritmo é executado de forma contínua e, a cada iteração, o identifica a estação com o maior <strong>ratio</strong> (melhor retorno sobre o investimento ponderado pela pontuação), 
                alocando um banco de baterias, subtraindo seu custo do recurso restante e atualizando a indisponibilidade restante da estação.
            </p>
            <p>
                O algoritmo é executado enquanto houver recurso disponível ou enquanto houver indisponibilidade entre
                as estações.
            </p>
        </div>
    ''', unsafe_allow_html=True)
    st.subheader('Variáveis e definições')
    st.latex(r'''
        \text{pontuação} = \left\{ \text{ }
        \begin{aligned}
        & 0.19 \times \text{pontuação autonomia} + 0.03 \times \text{pontuação tráfego dados} + 0.265 \times \text{pontuação hierarquia} \text{ } + \\
        & 0.095 \times \text{pontuação tmr} + 0.16 \times \text{pontuação idade bateria} + 0.12 \times \text{pontuação faturamento} + 0.14 \times \text{pontuação cliente}
        \end{aligned}
        \right.
    ''')
    st.markdown('''
        <div style='text-align: justify;'>
        </div>
    ''', unsafe_allow_html=True)
    col1, _ = st.columns([.18, .82])
    with col1:
        var_options = st.selectbox(
            label='Selecione o ano',
            label_visibility='collapsed',
            options=[
                'pontuação autonomia', 'pontuação tráfego dados', 'pontuação hierarquia',
                'pontuação tmr', 'pontuação idade bateria', 'pontuação faturamento',
                'pontuação cliente'
            ],
            index=0
        )
    if var_options == 'pontuação autonomia':
        data = {
            'Probabilidade (queda estação)': ['Muito Alta', 'Média', 'Baixa'],
            'Peso': [5, 3, 1],
            'Conceituação': [
                'Sem bateria e/ou sem autonomia para atender ao tempo de queda de energia', 
                'Pelo historico queda x autonomia site dispõe de autonomia suficiente', 
                'Autonomia excedente ou não calculada/sem historico de queda de energia'
            ]
        }
    elif var_options == 'pontuação tráfego dados':
        data = {
            'Volume': ['3º Quartil dos dados', '2º Quartil de dados', '1º Quartil de dados'],
            'Peso': [5, 3, 1],
            'Conceituação': [
                'Sites com maior volume de dados trafegados', 'Sites com trafego de dados intermediário', 
                'Sites com baixo volume de dados trafegados'
            ]
        }
    elif var_options == 'pontuação hierarquia':
        data = {
            'Severidade': ['Muito Crítico', 'Crítico', 'Severo', 'Moderado', 'Leve'],
            'Peso': [100, 90, 80, 70, 60],
            'Tipo de Estações': [
                'Predios de centrais, BSC e RNC Remotas e GPON', 'Estações com roteadores IpRAN ou com repetidores MW>=20 sites',
                'Estações concentradores com repetidores MW<20sites', 'Estações estratégicas e Monosites', 'Estações de ponta ou repetidores RF'
            ]
        }
    elif var_options == 'pontuação tmr':
        data = {
            'Probabilidade': ['3º Quartil dos dados', '2º Quartil de dados', '1º Quartil de dados'],
            'Peso': [5, 3, 1],
            'TMR': ['Sites com maior TMR', 'Sites com TMR mediano', 'Sites com TMR baixo']
        }
    elif var_options == 'pontuação idade bateria':
        data = {
            'Probabilidade': [
                'CHUMBO SELADA VRLA 12v >4 ANOS; CHUMBO SELADA VRLA 2v >5 ANOS; CHUMBO VENTILADA 2V >12 ANOS; LITIO >8 ANOS', 
                'DENTRO DA VIDA UTIL >1 ANO', 'DENTRO DA VIDA UTIL NO PRIMEIRO ANO'
            ],
            'Peso': [5, 3, 0],
            'Idade': ['Idade superior a vida útil estimada', 'Idade das baterias dentro da vida util a partir de 1 ano', 'Primeiro ano de vida da bateria']
        }
    elif var_options == 'pontuação faturamento':
        data = {
            'Probabilidade': ['3º Quartil do faturamento', '2º Quartil do faturamento', '1º Quartil do faturamento'],
            'Peso': [5, 3, 1],
            'Idade': ['Faturamento alto', 'Faturamento mediano', 'Faturamento baixo']
        }
    elif var_options == 'pontuação cliente':
        data = {
            'Severidade': ['ATENDE', 'SITES RESIDENCIAL e EMPRESARIAL', 'NÃO ATENDE'],
            'Peso': [5, 3, 1],
            'Tipo de Estações': [
                'Atende cliente corporativo, cliente VIP', 'Sites mercado residencial e empresarial', 
                'Site não atende clientes corporativos ou VIP'
            ]
        }
    st.dataframe(
        data=pd.DataFrame(data),
        hide_index=True,
        width='stretch' 
    )