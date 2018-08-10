# OpenStreetMap Data Case Study
**Wrangle OpenStreetMap Data Udacity Project**

**Author: [Arthur Vetori]

**Date: August 9, 2018**

## Map Area
[Manhattan, NY, United States](https://en.wikipedia.org/wiki/Manhattan)

I choose this area because I work in financial markets and this area is the financial center of the United States. One day I wish to go there.
I used mongodb over SQL for learning purposes. I think it would be a good idea to learn mongo.

## Problems Encountered in the Map
After initially downloading a small sample size of the map, I processed it in data.py and inserted in MongoDB to view a bit of the schema. I found out that

1. Some second level “k” tags separated by “.”

```xml
<tag k="cityracks.housenum" v="295"/>
<tag k="cityracks.large" v="0"/>
<tag k="cityracks.rackid" v="2410"/>
<tag k="cityracks.small" v="1"/>
<tag k="cityracks.street" v="Canal St"/>
```

This issue was solved replacing “.” For “:” over the tags

```python
# replace second level tags containing '.' to ':'
def replace_dot(text):
    return text.replace(".",":")
```

2. Second level name tags with multiple languages.

```xml
<tag k="name" v="Mott Street"/>
<tag k="name:en" v="Mott Street"/>
<tag k="name:zh" v="勿街"/>
```

When name is a dictionary instead of string, I consider the name[“en”] element


3. Misplaced value inside second level country tag

```xml
<tag k="tiger:county" v="New York, NY"/>
```

Because we are only analyzing a map inside United States, the country property is not useful.

4. Name abbreviations (ie: St, Ave, etc.)

```xml
<tag k="addr:street" v="E. 54th St."/>
```

In this case, I used a function to replace for the cases found in street names auditing.

```python
mapping = {"St": "Street",
           "St.": "Street",
           "Ave": "Avenue",
           "Ave.": "Avenue",
           "N.": "North",
           "W.": "West",
           "E": "East",
           "E.": "East",
           "Fdr": "Federal",
           "Streer": "Street",
           "Steet": "Street",
           "S": "South",
           "S.": "South",
           "Avene": "Avenue"
           }

# update name abbreviations
def update_name(name):
    for key in mapping:
        newname = re.sub(r'\b' + key + r'\b\.?', mapping[key], name)
    return newname

```python


## Overview of the Data

- ![Map Size](images/file_size.png)
- ![Number of unique users](images/unique_users.png)