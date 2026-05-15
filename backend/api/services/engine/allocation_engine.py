import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class Estacao:
    '''
    Representa uma estação candidata à alocação de recursos.

    Cada estação possui uma demanda histórica de indisponibilidade,
    um custo de intervenção e um ganho esperado por alocação.
    '''

    def __init__(
        self,
        nome_estacao: str,
        autonomia_projetada_estacao: int,
        carga_estacao: float,
        pontuacao_estacao: float,
        tecnologia_bateria: str,
        tensao_bateria:int,
        capacidade_bateria: int,
        custo_bateria: float,
        df_indisponibilidades: pd.DataFrame
    ):
        self.nome_estacao = nome_estacao
        self.autonomia_projetada_estacao = autonomia_projetada_estacao
        self.carga_estacao = carga_estacao
        self.pontuacao_estacao = pontuacao_estacao
        self.tecnologia_bateria = tecnologia_bateria
        self.tensao_bateria = tensao_bateria
        self.capacidade_bateria = capacidade_bateria
        self.custo_bateria = custo_bateria
        self.df_indisponibilidades = df_indisponibilidades.copy()
        self.historico_alocacoes: List[Dict[str, Any]] = []

    def get_indisponibilidade_total_restante(self) -> float:
        '''
        Realiza a soma total da indisponibilidade ainda não mitigada.

        Returns:
            float: Horas totais restantes.
        '''
        return self.df_indisponibilidades['indisponibilidade_horas'].sum()

    def get_ganho_marginal(self) -> float:
        '''
        Calcula o ganho máximo possível de uma nova alocação.

        Returns:
            float: Ganho potencial (horas reduzidas).
        '''
        if self.get_indisponibilidade_total_restante() <= 0:
            return 0.0

        melhoria_por_evento = np.minimum(
            self.capacidade_bateria / self.carga_estacao,
            self.df_indisponibilidades['indisponibilidade_horas'],
        )

        return melhoria_por_evento.sum()


    def apply_alocacao(self) -> float:
        '''
        Aplica uma rodada de alocação para a estação, atualizando a indisponibilidade 
        remanescente e registrando o histórico.

        Returns:
            float: Ganho efetivo obtido nesta rodada.
        '''
        melhoria_por_evento = np.minimum(
            self.capacidade_bateria / self.carga_estacao,
            self.df_indisponibilidades['indisponibilidade_horas'],
        )

        ganho_total = melhoria_por_evento.sum()

        self.df_indisponibilidades['indisponibilidade_horas'] = np.maximum(
            self.df_indisponibilidades['indisponibilidade_horas']
            - (self.capacidade_bateria / self.carga_estacao),
            0,
        )

        self.historico_alocacoes.append(
            {
                'custo_bateria': self.custo_bateria,
                'ganho': ganho_total,
                'indisponibilidade_restante': self.get_indisponibilidade_total_restante(),
            }
        )

        return ganho_total
    

def run_alocacoes(
    estacoes: List[Estacao],
    investimento: float,
) -> List[Dict[str, Any]]:
    '''
    Executa a alocação de recursos entre as estações.

    Em cada iteração, escolhe a estação com maior ratio: (pontuação × ganho marginal) / custo_bateria.

    Args:
        estacoes (List[Estacao]): Lista de estações.
        investimento (float): Orçamento disponível.

    Returns:
        List[Dict[str, Any]]: Log detalhado das alocações.
    '''
    investimento_restante = investimento
    alocacoes: List[Dict[str, Any]] = []

    while investimento_restante > 0:
        melhor_estacao = None
        melhor_indice = 0.0

        ganhos_acumulados = {
            estacao.nome_estacao: sum(a['ganho'] for a in estacao.historico_alocacoes)
            for estacao in estacoes
        } #=> retirando pois a trava não aproveita o investimento total disponível

        for estacao in estacoes:
            if (
                estacao.get_indisponibilidade_total_restante() > 0
                and ganhos_acumulados[estacao.nome_estacao] 
                < estacao.autonomia_projetada_estacao #=> retirando pois a trava não aproveita o investimento total disponível
            ):
                ganho = estacao.get_ganho_marginal()

                if ganho <= 0:
                    continue

                indice = (
                    estacao.pontuacao_estacao * ganho
                ) / estacao.custo_bateria

                if indice > melhor_indice and investimento_restante >= estacao.custo_bateria:
                    melhor_indice = indice
                    melhor_estacao = estacao

        if melhor_estacao is None:
            break

        ganho = melhor_estacao.apply_alocacao()
        investimento_restante -= melhor_estacao.custo_bateria

        alocacoes.append(
            {
                'estacao': melhor_estacao.nome_estacao,
                'autonomia_projetada': melhor_estacao.autonomia_projetada_estacao,
                'rodada_alocacao': len(melhor_estacao.historico_alocacoes),
                'tecnologia': melhor_estacao.tecnologia_bateria,
                'tensao': melhor_estacao.tensao_bateria,
                'capacidade': melhor_estacao.capacidade_bateria,
                'custo': melhor_estacao.custo_bateria,
                'ganho': ganho,
                'ganho_por_custo': ganho / melhor_estacao.custo_bateria,
                'investimento_restante': investimento_restante,
                'indisponibilidade_restante': melhor_estacao.get_indisponibilidade_total_restante(),
            }
        )

    return alocacoes


def run_allocation_engine(
    df: pd.DataFrame,
    df_indisponibilidades: pd.DataFrame,
    investimento: float = 1000000,
) -> pd.DataFrame:
    '''
    Inicializa as estações e executa o processo de alocação.

    Args:
        df (pd.DataFrame): Features das estações prioritárias.
        df_indisponibilidades (pd.DataFrame): Histórico de indisponibilidades.
        investimento (float): Orçamento total disponível.

    Returns:
        pd.DataFrame: Log estruturado de todas as alocações realizadas.
    '''
    estacoes: List[Estacao] = []

    for _, row in df.iterrows():
        df_indisp_estacao = df_indisponibilidades[
            df_indisponibilidades['estacao'] == row['estacao']
        ][['estacao', 'indisponibilidade_horas']].copy()

        estacao = Estacao(
            nome_estacao=row['estacao'],
            autonomia_projetada_estacao=row['autonomia_projetada'],
            carga_estacao=row['carga'],
            pontuacao_estacao=row['pontuacao'],
            tecnologia_bateria=row['tecnologia'],
            tensao_bateria=row['tensao'],
            capacidade_bateria=row['capacidade'],
            custo_bateria=row['custo'],
            df_indisponibilidades=df_indisp_estacao
        )

        estacoes.append(estacao)

    df = pd.DataFrame(run_alocacoes(estacoes, investimento))

    return df


if __name__ == '__main__':
    run_allocation_engine()