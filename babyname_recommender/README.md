## Baby Name Recommender

My blog post on the creation of the database can be found <a href="https://a-n-rose.github.io/2018/11/05/updated-babyname-recommender.html">here</a>.

Currently my scripts only set up a database with 2 tables:

1) 'names': name_id, name, sex

2) 'popularity': year_id, year, popularity, name_id

Additional scripts will be added for building a recommendation system.

### Getting started

Dowload my scripts (which are in the works) into the directory you want to create this recommendation system.

### Create subdirectory for storing text files with name data

In the directory where the scipts are, create a subdirectory called 'names'.

Download the zip file 'names.zip', made available from social security applications in the USA onwards of 1879. The most update version can be found <a href="https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-level-data">here</a>. Unzip this contents into the subdirectory 'names'. Otherwise you'll end up with text files filling in whatever directory you saved that zip file to. 

The structure of the name data is clarified in the NationalReadMe.pdf included in the zip file.

### Create Virtual Environment

```
$ python3 -m venv env
$ source env/bin/activate
(env)...$
```

### Install dependencies

```
(env)...$ pip install Numpy
```

### Run the progam
```
(env)...$ python3 database_setup.py

```
