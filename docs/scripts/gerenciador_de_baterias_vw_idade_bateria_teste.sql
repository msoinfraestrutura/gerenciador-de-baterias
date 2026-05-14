-- db_infra_am.gerenciador_de_baterias_vw_idade_bateria_teste fonte

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `db_infra_am`.`gerenciador_de_baterias_vw_idade_bateria_teste` AS
select
    `ts`.`nome` AS `estacao`,
    `tbr`.`tipo_bateria` AS `tipo_bateria`,
    `tbr`.`dt_fabricacao` AS `data_fabricacao`,
    `tbr`.`dt_instalacao` AS `data_instalacao`,
    `tbr`.`tensao` AS `tensao`,
    `tbr`.`qtde` AS `quantidade`,
    `tbr`.`amper_hora` AS `capacidade`
from
    ((`db_infra_am`.`tbl_site` `ts`
left join `db_infra_am`.`tbl_retificador` `tr` on
    ((`tr`.`id_site` = `ts`.`id`)))
left join `db_infra_am`.`tbl_baterias_retificador` `tbr` on
    ((`tbr`.`id_retificador` = `tr`.`id`)))
where
    ((`tbr`.`dt_instalacao` is not null)
        and (`tbr`.`tipo_bateria` is not null)
            and (`tbr`.`tensao` is not null)
                and (`tbr`.`qtde` is not null)
                    and (`tbr`.`amper_hora` is not null));