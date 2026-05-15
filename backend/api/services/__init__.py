import os
from dotenv import load_dotenv


load_dotenv()

SSH_HOST = '189.23.51.118'
SSH_USER = 'mso001'
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

MYSQL_DB_HOST = '127.0.0.1'
MYSQL_DB_PORT = 3306
MYSQL_DB_NAME_1 = 'db_infra_am'
MYSQL_DB_NAME_2 = 'db_admin_infratel'
MYSQL_DB_USER = 'admin'
MYSQL_DB_PASSWORD = os.getenv('MYSQL_DB_PASSWORD')
MYSQL_LOCAL_PORT_TUNNEL = 6542

PG_DB_HOST = '127.0.0.1'
PG_DB_PORT = 5432
PG_DB_NAME_1 = 'db_smartplan'
PG_DB_NAME_2 = 'db_incidentes'
PG_DB_USER = 'admin'
PG_DB_PASSWORD = 'claro@25'
PG_LOCAL_PORT_TUNNEL = 6543

MYSQL_SQL_QUERY_1 = 'SELECT * from gerenciador_de_baterias_vw_fontes;'
MYSQL_SQL_QUERY_2 = 'SELECT * from gerenciador_de_baterias_vw_idade_bateria_teste;'
MYSQL_SQL_QUERY_3 = 'SELECT * from gerenciador_de_baterias_vw_autonomia_inventario;'
MYSQL_SQL_QUERY_4 = '''
    SELECT
        ts.nome AS estacao,
        CASE
            WHEN COUNT(st.id) = 0 THEN 'SEM GERADOR'
            WHEN COUNT(st.id) = 1 THEN 'SINGELO'
            ELSE 'REDUNDANTE'
        END AS gerador
    FROM db_infra_am.tbl_site AS ts
    LEFT JOIN db_infra_am.tbl_gerador AS tg
        ON tg.id_site = ts.id
    LEFT JOIN db_infra_am.tbl_status_gerador AS st
        ON st.id = tg.id_status
        AND st.nome = 'ATIVO'
    WHERE ts.site_ativo = 'ATIVO'
    GROUP BY ts.nome;
'''
PG_SQL_QUERY_1 = '''
    SELECT
        te.nome AS estacao,
        CASE 
            WHEN REPLACE(te.regional, 'CLARO ', '') = 'PR/SC' 
                THEN te.estado
            ELSE REPLACE(te.regional, 'CLARO ', '')
        END AS cluster,
        te.estado AS uf,
        te.municipio,
        te.ibge,
        te.alias_ebt,
        te.nome_ref_estacao,
        te.severidade_omr,
        te.finalidade_movel,
        te.finalidade_empresarial,
        te.finalidade_residencial,
        te.anatel_rf,
        te.anatel_nextel_rf,
        te.latitude,
        te.longitude
    FROM tb_estacoes te
    WHERE
        te.status IN ('Mobilizada', 'Em Desmobilização')
        AND UPPER(RIGHT(TRIM(te.nome), 1)) NOT IN ('F', 'R', 'S', 'W');
'''
PG_SQL_QUERY_2 = '''
    SELECT 
        incident_number, 
        site_ci AS estacao, 
        ic, 
        generic_categorization_tier_1, 
        filtro_classificacoes_1, 
        state_or_province, 
        submit_date, 
        clear_date, 
        resolved_date, 
        filtro_equipe_2,
        mttr
    FROM tb_indisponibilidade
    WHERE EXTRACT(YEAR FROM SUBMIT_DATE) <= 2025;
'''
PG_SQL_QUERY_3 = '''
    SELECT 
        incident_number, 
        site_ci AS estacao,
        categorization_tier_3, 
        submit_date, 
        clear_date, 
        resolved_date
    FROM tb_alarmes
    WHERE EXTRACT(YEAR FROM SUBMIT_DATE) <= 2025;
'''
PG_SQL_QUERY_4 = '''
    WITH horas_ano AS (
        SELECT 
            DISTINCT EXTRACT(year FROM tb_indisponibilidade.submit_date)::text AS ano,
            EXTRACT(epoch FROM date_trunc('year'::text, tb_indisponibilidade.submit_date) + '1 year'::interval - date_trunc('year'::text, tb_indisponibilidade.submit_date)) / 3600.0 AS total_horas
        FROM tb_indisponibilidade
        WHERE tb_indisponibilidade.submit_date IS NOT NULL
        ), 
        indisponibilidades AS (
            SELECT EXTRACT(year FROM tbi.submit_date)::text AS ano,
            tbi.site_ci AS estacao,
            sum(tbi.mttr)::numeric / 3600.0 AS mttr_horas,
            sum(
                CASE
                    WHEN lower(tbi.generic_categorization_tier_1::text) <> ALL (ARRAY['energia concessionária'::text, 'energia concessionaria'::text]) THEN tbi.mttr
                    ELSE 0
                END)::numeric / 3600.0 AS mttr_horas_parcial,
            sum(
                CASE
                    WHEN lower(tbi.generic_categorization_tier_1::text) = ANY (ARRAY['energia concessionária'::text, 'energia concessionaria'::text]) THEN tbi.mttr
                    ELSE 0
                END)::numeric / 3600.0 AS mttr_horas_energia,
            count(DISTINCT tbi.incident_number) AS incidentes,
            count(DISTINCT
                CASE
                    WHEN lower(tbi.generic_categorization_tier_1::text) <> ALL (ARRAY['energia concessionária'::text, 'energia concessionaria'::text]) THEN tbi.incident_number
                    ELSE NULL::character varying
                END) AS incidentes_parcial,
            count(DISTINCT
                CASE
                    WHEN lower(tbi.generic_categorization_tier_1::text) = ANY (ARRAY['energia concessionária'::text, 'energia concessionaria'::text]) THEN tbi.incident_number
                    ELSE NULL::character varying
                END) AS incidentes_energia
            FROM tb_indisponibilidade tbi
            WHERE tbi.site_ci::text <> ''::text AND tbi.mttr > 0
            GROUP BY (EXTRACT(year FROM tbi.submit_date)::text), tbi.site_ci
        )
    SELECT i.ano,
        i.estacao,
        ((ha.total_horas - i.mttr_horas) / ha.total_horas * 100)::numeric(10,2) AS disponibilidade,
        ((ha.total_horas - i.mttr_horas_parcial) / ha.total_horas * 100)::numeric(10,2) AS disponibilidade_parcial,
        ((ha.total_horas - i.mttr_horas_energia) / ha.total_horas * 100)::numeric(10,2) AS disponibilidade_energia,
        (i.mttr_horas)::numeric(10,2) AS indisponibilidade_horas,
        (i.mttr_horas_parcial)::numeric(10,2) AS indisponibilidade_parcial_horas,
        (i.mttr_horas_energia)::numeric(10,2) AS indisponibilidade_energia_horas,
        CASE
            WHEN i.mttr_horas = 0::numeric THEN 0::numeric(10,2)
            ELSE (i.mttr_horas_energia / i.mttr_horas * 100)::numeric(10,2)
        END AS indisponibilidade_energia,
        ((ha.total_horas - i.mttr_horas) / ha.total_horas * 100)::numeric(10,2) - 99.65 AS diferenca_meta_disponibilidade,
        ((ha.total_horas - i.mttr_horas_parcial) / ha.total_horas * 100)::numeric(10,2) - 99.65 AS diferenca_meta_disponibilidade_parcial,
        ((ha.total_horas - i.mttr_horas_energia) / ha.total_horas * 100)::numeric(10,2) - 99.65 AS diferenca_meta_disponibilidade_energia,
        i.incidentes,
        i.incidentes_parcial,
        i.incidentes_energia
    FROM indisponibilidades i
        JOIN horas_ano ha ON ha.ano = i.ano
    ORDER BY i.ano, i.estacao;
'''