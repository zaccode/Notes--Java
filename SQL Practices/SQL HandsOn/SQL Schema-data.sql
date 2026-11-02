
-- Insert Sample Data
INSERT INTO employees VALUES
(1,'Aarav Sharma',28,'M',75000,'IT','Senior Developer',NULL,'2020-01-15','Mumbai',10000,4),
(2,'Priya Patel',32,'F',65000,'HR','HR Manager',1,'2019-03-20','Delhi',8000,5),
(3,'Rahul Singh',45,'M',85000,'Finance','Finance Head',1,'2018-07-10','Mumbai',15000,8),
(4,'Neha Gupta',29,'F',72000,'IT','Developer',1,'2021-02-01','Bangalore',9000,3),
(5,'Vikram Reddy',38,'M',90000,'IT','Team Lead',1,'2017-11-25','Delhi',12000,6),
(6,'Ananya Menon',27,'F',60000,'HR','HR Executive',2,'2022-06-15','Mumbai',5000,2),
(7,'Karthik Nair',51,'M',95000,'IT','Architect',1,'2015-09-30','Bangalore',20000,10),
(8,'Meera Krishnan',33,'F',68000,'Marketing','Marketing Lead',5,'2020-08-12','Delhi',7000,4),
(9,'Arjun Reddy',42,'M',82000,'IT','Senior Developer',5,'2016-12-01','Mumbai',11000,7),
(10,'Sneha Patel',26,'F',58000,'Marketing','Marketing Executive',8,'2023-01-20','Bangalore',4000,1),
(11,'Rajesh Kumar',39,'M',70000,'Finance','Financial Analyst',3,'2019-06-10','Chennai',6000,5),
(12,'Deepa Iyer',34,'F',64000,'HR','HR Specialist',2,'2020-11-15','Hyderabad',5500,4),
(13,'Suresh Babu',47,'M',88000,'IT','Solution Architect',5,'2014-03-01','Chennai',18000,10),
(14,'Kavya Nair',31,'F',67000,'Finance','Accountant',3,'2021-08-20','Hyderabad',5000,3),
(15,'Ravi Teja',44,'M',91000,'IT','Technical Manager',1,'2016-07-15','Mumbai',16000,8);

INSERT INTO departments VALUES
(1,'IT','Mumbai',5000000),
(2,'HR','Delhi',2000000),
(3,'Finance','Mumbai',3000000),
(4,'Marketing','Bangalore',2500000),
(5,'Operations','Pune',3500000);

INSERT INTO projects VALUES
(1,'AI Implementation','IT','Active','2024-01-01','2024-12-31',1500000),
(2,'Employee Portal','IT','Completed','2023-06-01','2023-12-31',800000),
(3,'Financial Audit','Finance','Active','2024-02-01','2024-08-31',500000),
(4,'Market Research','Marketing','Planning','2024-03-01','2024-09-30',300000),
(5,'Cloud Migration','IT','Active','2024-01-15','2024-11-30',2000000),
(6,'Talent Acquisition','HR','Completed','2023-10-01','2024-01-31',400000);

INSERT INTO customers VALUES
(1,'TechCorp','Mumbai','2023-01-10','tech@corp.com'),
(2,'GlobalSolutions','Delhi','2023-02-15','info@global.com'),
(3,'InnovationLabs','Bangalore','2023-03-20','contact@innovate.com'),
(4,'AlphaInc','Mumbai','2023-04-25','alpha@inc.com'),
(5,'BetaSystems','Pune','2023-05-30','beta@systems.com'),
(6,'GammaTech','Chennai','2023-06-10','gamma@tech.com'),
(7,'DeltaCorp','Hyderabad','2023-07-05','delta@corp.com'),
(8,'EpsilonSoft','Bangalore','2023-08-15','epsilon@soft.com'),
(9,'ThetaSolutions','Delhi','2023-09-20','theta@solutions.com'),
(10,'OmegaLabs','Mumbai','2023-10-01','omega@labs.com');

INSERT INTO orders VALUES
(101,1,'2024-01-10',15000,'Completed','Electronics'),
(102,1,'2024-01-15',23000,'Pending','Software'),
(103,2,'2024-01-20',12000,'Completed','Hardware'),
(104,3,'2024-02-01',50000,'Completed','Electronics'),
(105,3,'2024-02-05',18000,'Cancelled','Software'),
(106,4,'2024-02-10',32000,'Completed','Hardware'),
(107,5,'2024-02-15',45000,'Pending','Electronics'),
(108,6,'2024-03-01',21000,'Completed','Software'),
(109,7,'2024-03-05',67000,'Completed','Electronics'),
(110,8,'2024-03-10',34000,'Completed','Hardware'),
(111,9,'2024-03-15',28000,'Pending','Software'),
(112,10,'2024-04-01',42000,'Completed','Electronics'),
(113,1,'2024-04-05',15000,'Completed','Hardware'),
(114,2,'2024-04-10',33000,'Completed','Software'),
(115,3,'2024-04-15',29000,'Pending','Electronics');

INSERT INTO products VALUES
(1,'Laptop Pro','Electronics',75000,50),
(2,'Wireless Mouse','Accessories',1500,200),
(3,'27" Monitor','Electronics',25000,30),
(4,'Mechanical Keyboard','Accessories',5000,100),
(5,'Enterprise Software','Software',100000,20),
(6,'External SSD','Electronics',12000,60),
(7,'Webcam HD','Accessories',3000,80),
(8,'Cloud Storage Plan','Software',50000,15),
(9,'Printer','Electronics',15000,40),
(10,'USB Hub','Accessories',2000,150);

INSERT INTO order_items VALUES
(1,101,1,2,75000),
(2,101,2,1,1500),
(3,102,5,1,100000),
(4,103,3,1,25000),
(5,104,1,1,75000),
(6,104,6,2,12000),
(7,105,5,1,100000),
(8,106,3,2,25000),
(9,107,1,3,75000),
(10,108,8,1,50000),
(11,109,1,2,75000),
(12,110,6,2,12000),
(13,111,5,1,100000),
(14,112,1,1,75000),
(15,113,4,1,5000);