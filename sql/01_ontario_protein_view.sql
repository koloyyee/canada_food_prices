drop view if exists view_ontario_protein_prices;

create view view_ontario_protein_prices as -- 1. farm products prices
with farm_mapped as (
    select
        'farm' as stage,
        month,
        price_per_unit,
        uom,
        product,
        case
            when lower(product) like '%heifers for slaughter%' then 'beef'
            when lower(product) like '%steers for slaughter%' then 'beef'
            when lower(product) like '%hog%' then 'pork'
            when lower(product) like '%chicken%' then 'chicken'
            when lower(product) like '%egg%' then 'egg'
            when lower(product) like '%milk%' then 'milk'
            else null
        end as protein
    from
        farm_prod_prices fpp
    where
        geo = 'Ontario'
        and month >= '2019-01'
),
-- retail prices 
retail_mapped as (
    select
        'retail' as stage,
        month,
        product,
        uom,
        price_per_unit,
        case
            when lower(product) like '%beef%' then 'beef'
            when lower(product) like '%pork%' then 'pork'
            when lower(product) like '%bacon%' then 'pork'
            when lower(product) like '%chicken%' then 'chicken'
            when lower(product) like '%egg%' then 'egg'
            when lower(product) like 'milk%' then 'milk'
            else null
        end as protein
    from
        retail_prices rp
    where
        geo = 'Ontario'
        and month >= '2019-01'
),
-- 3. unified output
combined_mapped as (
    select
        month,
        stage,
        product,
        protein,
        price_per_unit,
        uom
    from
        farm_mapped
    where
        protein is not null
    union
    all
    select
        month,
        stage,
        product,
        protein,
        price_per_unit,
        uom
    from
        retail_mapped
    where
        protein is not null
) -- 4. Normalise price per unit and uom
select
    month,
    stage,
    protein,
    product,
    price_per_unit,
    uom,
    case
        when lower(uom) = lower('dollars per hundredweight') then round(price_per_unit / 45.3592, 2)
        when lower(uom) = lower('dollars per kilolitre') then round(price_per_unit / 1000.0, 2)
        when lower(product) like lower('%bacon, 500 grams%') then round(price_per_unit * 2.0, 2)
        when lower(product) like lower('%milk, 2 litres%') then round(price_per_unit / 2.0, 2)
        when lower(product) like lower('%milk, 4 litres%') then round(price_per_unit / 4.0, 2)
        else price_per_unit
    end as normalised_price,
    case
        when lower(uom) = lower('dollars per hundredweight') then 'Dollars per kg'
        when lower(uom) = lower('dollars per kilolitre') then 'Dollars per litre'
        when lower(product) like lower('%bacon, 500 grams%') then 'Dollars per kg'
        when lower(product) like lower('%milk%') then 'Dollars per litre'
        else uom
    end as normalised_uom
from
    combined_mapped
where
    protein is not null
order by
    month;