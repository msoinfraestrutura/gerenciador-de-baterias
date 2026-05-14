-- db_infra_am.gerenciador_de_baterias_vw_autonomia_inventario fonte

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `gerenciador_de_baterias_vw_autonomia_inventario` AS with `capacidade` as (
select
    `tbr`.`id_retificador` AS `id_retificador`,
    `ts`.`nome` AS `estacao`,
    regexp_replace(`tbr`.`tipo_bateria`, '\\*$', '') AS `tecnologia`,
    `tfb`.`nome` AS `fabricante`,
    `tbr`.`tensao` AS `tensao`,
    `tbr`.`qtde_instalada` AS `quantidade`,
    sum(`tbr`.`amper_hora`) AS `capacidade`
from
    (((`tbl_site` `ts`
join `tbl_retificador` `tr` on
    ((`tr`.`id_site` = `ts`.`id`)))
join `tbl_baterias_retificador` `tbr` on
    ((`tbr`.`id_retificador` = `tr`.`id`)))
join `tbl_fabricante_bateria` `tfb` on
    ((`tfb`.`id` = `tbr`.`id_fabricante`)))
group by
    `tbr`.`id_retificador`,
    `ts`.`nome`,
    `tbr`.`tipo_bateria`,
    `tfb`.`nome`,
    `tbr`.`tensao`,
    `tbr`.`qtde_instalada`),
`potencia` as (
select
    `sub`.`id_retificador` AS `id_retificador`,
    `sub`.`potencia_instalada` AS `potencia_instalada`
from
    (
    select
        `tpf`.`idPreventiva` AS `id_retificador`,
        (case
            when regexp_like(trim(`tpf`.`consumo_dc`), '^[0-9]+([.,][0-9]+)?$') then cast(replace(`tpf`.`consumo_dc`, ',', '.') as decimal(10, 2))
            else NULL
        end) AS `potencia_instalada`,
        row_number() OVER (PARTITION BY `tpf`.`idPreventiva`
    ORDER BY
        `tpf`.`data_preventiva` desc,
        `tpf`.`id` desc ) AS `rn`
    from
        `tbl_preventiva_fonte` `tpf`) `sub`
where
    (`sub`.`rn` = 1))
select
    `c`.`estacao` AS `estacao`,
    `c`.`tecnologia` AS `tecnologia`,
    `c`.`fabricante` AS `fabricante`,
    `c`.`tensao` AS `tensao`,
    `c`.`quantidade` AS `quantidade`,
    `c`.`capacidade` AS `capacidade`,
    ((0.8 * (10 * pow((`c`.`capacidade` / 10.0), 1.35))) / pow(`p`.`potencia_instalada`, 1.35)) AS `autonomia_horas`
from
    (`capacidade` `c`
join `potencia` `p` on
    ((`p`.`id_retificador` = `c`.`id_retificador`)))
where
    (`p`.`potencia_instalada` > 0)
order by
    `c`.`estacao`,
    `c`.`fabricante`,
    `c`.`tecnologia`;