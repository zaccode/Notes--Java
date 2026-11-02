select * from employees;
-- 1. row_number() sequence continous when the same value occoured in salary 
select name, salary,
	row_number() over(order by salary desc) 
    from employees;


-- 2. rank()  sequence not be continous  when the same value occoured in salary 
select name, salary,
rank() over (order by salary asc)
from employees;

-- 3. dense_rank  sequence skip but continous after the same value occoured in salary 
select name,salary,
	dense_rank() over (order by salary desc) from employees;
    
select name,department, salary,
first_value(name) over (partition by department order by salary)
from employees;

select name,department, salary,
last_value(name) over(partition by department order by salary
	rows between unbounded preceding and unbounded following
    ) 
    from employees;

select name,salary,
	ntile(4) over(order by salary)
    from employees;

select name,salary,
sum(salary) over (order by emp_id)
from employees;

select name,salary,
avg(salary) over(order by emp_id rows between 2 preceding and current row) from employees;

with ranked as (
	select name,department,salary,
    dense_rank() over(partition by department order by salary desc) as dr
    from employees
)
select department,name,salary,dr from ranked where dr <= 3;

with ranked as(
select name,department,salary,
rank() over(partition by department order by salary) as rn
from employees
)

select department,name,salary from ranked where rn = 1;

select name,salary,
lag(salary) over(order by salary),
salary - lag(salary) over(order by salary)
from employees;

select name,salary,
lead(salary) over (order by salary),
lead(salary) over(order by salary) - salary
from employees;

select date_format(order_date,'%Y-%m') as month,
sum(amount) as total_sales,
lag(sum(amount)) over(order by date_format(order_date,'%Y-%m')) as prev_month_sales,
(sum(amount) - lag(sum(amount)) over(order by date_format(order_date,'%Y-%m')))/
(lag(sum(amount)) over(order by date_format(order_date,'%Y-%m')) * 100)  as growth_percent
-- (sum(amount) - lag(sum(amount)) over(order by date_format(order_date,'%Y-%m'))),
-- lag(sum(amount)) over(order by date_format(order_date,'%Y-%m')) 
from orders group by date_format(order_date,'%Y-%m');

select order_date,
sum(amount),
sum(sum(amount)) over(order by order_date) as cumulative_sum
from orders
group by order_date order by order_date;

select c.customer_id,c.name, sum(o.amount),rank() over (order by sum(o.amount) desc) as customer_rank
from customers c join orders o on c.customer_id = o.customer_id group by c.customer_id,c.name;
