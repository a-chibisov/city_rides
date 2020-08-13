# City rides 
Welcome to the Micromobility Vehicles profitability and perfomance analysis app.

# Prerequisites
You need a running Docker and a browser (or http requests processing tool).

# How to use
1. Clone the git repository to your computer.
2. Open your command line and navigate to the cloned project directory.
3. Run <code>docker-compose up -d --build</code>.
4. When the docker containers are built and started wait about 1 minute for database 
initial load scripts to be completed and navigate to the start page http://localhost:5000/.
5. All further instructions are given on the start page.
6. Run <code>docker-compose down -v</code> after you finish your work.

# Technical description
I use Docker to build the app and run the initial setup processes. This is the most convenient way for you to easily 
run and use the app on almost any platform.<br><br>
I use Python SQLAlchemy lib to build the database and load initial data there. This is the most convenient way to define 
and fill the relational data model (and we`re having relational data in our source files). I have created a copy for 
each given source file with several records from them to demonstrate the duplicates logging feature. Duplicates are 
logged into the database table and then can be called with an API.<br><br>
I use PostgreSQL to store and prepare the analytical view of the data using its functions. This is the most convenient 
way to analyze modest-sized relational data and this is the language I have the most expertise in. As far as I could 
understand the task, we actually need to show the last 5 rides (the latest deployments go first, rides are also ordered 
by their start time in descending order) with some of their attributes. A table with vehicle id, its QR code and
analytical data in JSON format is filled on the app start, indexed and ready to be used.<br><br>
I use Python Flask to run a web-server and let the user communicate with the database via API, which is described 
on the starting page. This is the most convenient way to run a simple web-server for a prototype like this.
Analysis data is returned in a JSON format as the format was not specified, and JSON is more or less suitable for
many use cases.<br><br>
There is also a small stress-test Python script which can be called via API to check the time needed to process 5000
subsequent requests, and a unittest script to compare the number of records in source files and in the database 
(including duplicates log), it can also be called via API.
