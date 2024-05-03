![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

#### Project Status
Currently, this project is on pause as I explore other avenues for learning and growth.

# immo-eliza-airflow

Within this project, we've developed a streamlined pipeline orchestration using Airflow. This sophisticated system facilitates the seamless scheduling of model training and updates, building upon the foundation laid in a previous project available [here](https://github.com/DedeyJ/immo-eliza-ml). 

## Installation

To establish our Airflow environment, we rely on Docker and Docker Compose for seamless setup. For a hassle-free experience, I highly recommend utilizing [Docker Desktop](https://www.docker.com/products/docker-desktop/).

To begin, download or clone this repository onto your local machine. Within the folder containing the docker-compose and Dockerfile, navigate to the command line interface (CLI) and follow these steps:

- Setting the right Airflow user (Linux only)
~~~
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
~~~

For Windows I included an .env file that sets AIRFLOW_UID=50000.

- Initializing the database

~~~
docker compose up airflow-init
~~~

If everything went well, you should see following message:
~~~
airflow-init_1       | Upgrades done
airflow-init_1       | Admin user airflow created
airflow-init_1       | 2.9.0
start_airflow-init_1 exited with code 0
~~~

- Running Airflow
~~~
docker compose  up
~~~

If everything went accordingly, your folder structure on your local machine should now look like this:
~~~

├README.md
├.env
├docker-compose.yaml
├Dockerfile
├─config
├─plugins
├─logs
├─dags
└─project
    ├CustomTransformer.py
    ├training.py
    ├─model
    └─data
	└properties.csv
~~~

Now should be able to access your airflow webinterface by using any browser and using the link 
~~~
http://localhost:8080
~~~
![Login](images\airflow-login.jpg)
loging and password is both **airflow**.

![Main](images\airflow-main.jpg)

## DAG

![DAG](images\DAG_train_model.png)
In the diagram provided, you'll find a visual breakdown of the steps within my DAG. Below, we'll delve into each component:

- file_sensor: This SensorOperator within the DAG is designed to scan the designated folder (./project/data) for the presence of 'properties.csv'. Currently configured to execute this check every minute for a total of three times.

- branch_task: Serving as a PythonBranchOperator, this task enables task branching based on specific conditions. It revisits the existence of 'properties.csv' and directs subsequent actions accordingly: sending an email if the file is absent, or proceeding to the model training phase if it's present.

- send_email: Utilizing the EmailOperator, this task dispatches an email notification in the event that the 'properties.csv' file is not found.

- train_model: Implemented as a BashOperator, this task executes the 'train.py' script located in the project folder. Upon completion, it generates both 'preprocess.pkl' and 'model.pkl' files in the designated model folder.

- copy_and_rename_file_task: This PythonOperator facilitates file manipulation by copying specified files and appending a date to their filenames for versioning purposes. By default, the copied and renamed files reside in their original folders, but the DAG allows for alternative directory specifications if necessary. The files subject to copying and renaming include 'properties.csv', 'preprocess.pkl', and 'model.pkl'.

## Volume

|Local Directory|Docker Directory|
|---------------|----------------|
|${AIRFLOW_PROJ_DIR:-.}/dags|/opt/airflow/dags|
|${AIRFLOW_PROJ_DIR:-.}/logs|/opt/airflow/logs|
|${AIRFLOW_PROJ_DIR:-.}/config|/opt/airflow/config|
|${AIRFLOW_PROJ_DIR:-.}/plugins|/opt/airflow/plugins|
|${AIRFLOW_PROJ_DIR:-.}/project|/model_training_project|
|${AIRFLOW_PROJ_DIR:-.}/project/data|/model_training_project/data|
|${AIRFLOW_PROJ_DIR:-.}/project/model|/model_training_project/model|

I've designed the structure in this manner to enhance visibility and ease of use on my local machine. Adding or removing DAGs is a straightforward process—simply drop them into the designated "dags" folder. Additionally, this setup offers the convenience of modifying the train.py model directly from my local machine, providing flexibility for adjustments as needed.

## Roadmap

Future prospects include:

- Integrating scraping into the orchestration process.
- Implementing automatic updates by pushing the 'model.pkl' file to a separate repository, where a streamlit app is deployed on Render.

## Timeline
Completion of this project spanned five days, encompassing both development efforts and the setup of Airflow through Docker Compose.

## Authors and acknowledgment
Author: [Jens Dedeyne](https://www.linkedin.com/in/jens-dedeyne/)
Acknowledgment: To my colleagues at the BeCode training camp for serving as a sounding board for innovative ideas.