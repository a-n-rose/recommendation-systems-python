## Baby Name Recommender

My blog post on the creation of the database can be found <a href="https://a-n-rose.github.io/2018/11/05/updated-babyname-recommender.html">here</a>.

Currently my scripts 

1) set up a database organizing US Name data into 2 tables and 

2) allows user to:
* create an account 
* create multiple searches (i.e. rate names for a daughter/ son/ dog/ etc.)
* rate names based on gender (or not)

## Database structure: 

Tables: 'names', 'popularity', 'users', 'ratinglists', 'ratings'

### Name data 

1) 'names': columns:
* name_id 
* name
* sex

2) 'popularity': columns
* year_id 
* year
* popularity 
* name_id (link to the names table)

### User data

3) 'users' : columns 
* user_id
* username
* password (not protected)

4) 'ratinglists': columns
* ratinglist_id
* ratinglist_name
* babyname_type (all, girl, boy)
* ratinglist_order (user's 1st, 2nd, etc) 
* ratinglist_user_id (user_id - link to users table)

5) 'ratings' : columns
* rating_id
* rating
* rating_ratinglist_id (ratinglist_id - links to the list)
* rating_name_id (name_id - links to the name)

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

### Run the progam to setup the database.
```
(env)...$ python3 database_setup.py

```
### Create the IPA features

```
(env)...$ python3 create_ipa_features.py
```

### Run the program to setup clustering based on features
```
(env)...$ python3 features_run.py
```

### To collect ratings:
Run *after* the database has been set up!

```
(env)...$ python3 babyname_run.py
```

## ToDo:

### In general
* unittests

### Babyname Rating Collector
* Add 'undo' functionality
* Add name search functionality
* Add recommender functionality 
* Add functionality to rate only non-rated names
