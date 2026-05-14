-- db_infra_am.gerenciador_de_baterias_vw_fontes fonte

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `db_infra_am`.`gerenciador_de_baterias_vw_fontes` AS with `RankedPreventivas` as (
select
    `ts`.`nome` AS `estacao`,
    cast(`tpf`.`consumo_dc` as decimal(10, 2)) AS `carga`,
    row_number() OVER (PARTITION BY `ts`.`nome`,
    `tr`.`id`
ORDER BY
    `tpf`.`data_preventiva` desc ) AS `rn`
from
    ((`db_infra_am`.`tbl_site` `ts`
left join `db_infra_am`.`tbl_retificador` `tr` on
    ((`tr`.`id_site` = `ts`.`id`)))
left join `db_infra_am`.`tbl_preventiva_fonte` `tpf` on
    ((`tpf`.`idPreventiva` = `tr`.`id`)))
where
    (`tpf`.`consumo_dc` is not null))
select
    `RankedPreventivas`.`estacao` AS `estacao`,
    `RankedPreventivas`.`carga` AS `carga`
from
    `RankedPreventivas`
where
    (`RankedPreventivas`.`rn` = 1);