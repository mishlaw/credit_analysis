select * from credit_data limit 10;

--общее количество кредитов
SELECT COUNT(*) AS total_loans FROM credit_data;

--общая сумма кредитов
select SUM(amount) as total_amount from credit_data;

--средняя сумма кредитов
select round(avg(amount),2) as avg_amount from credit_data;

--количество просроченных кредитов
select count(*) as overdue_count from credit_data where default_status='yes' ;

--Доля просроченных кредитов(npl)
select round(count(*) filter (where default_status='yes') * 100 / count(*) ,2) 
as npl_percent
from credit_data ;

--Средний размер кредита по типу занятости
select job, count(*) as count, round(avg(amount),2) as avg_amount from credit_data group by job
order by count desc;


