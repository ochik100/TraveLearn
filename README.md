# TraveLearn

### Overview

TraveLearn creates a network representation of travelers in the United States based on their interactions with other travelers on TripAdvisor travel forums. Communities of like-minded individuals are identified amongst a graph of millions of travelers. When topics are extracted from each community, various travel concerns and interests are discovered. Companies are able to benefit from and cater to the concerns and interests of travelers by creating personalized marketing strategies.

---

*Community Detection and Topic Modeling on a Network of Travelers in the United States*

* Data Collection - BeautifulSoup & EC2
  * All data was collected from TripAdvisor's US Travel forums. I wrote a parallelized web scraper using BeautifulSoup and deployed it on an AWS EC2 instance to take advantage of their machines with multicore processors.
* Data Storage - MongoDB & S3 Bucket
  * The web scraper was inserting all the data into a Mongo database and backups were stored in an AWS S3 bucket as well.
* The Network of Travelers
* Community Detection
* Topic Modeling with NMF
* Data Visualization - Gephi

### Pipeline Visualized
![alt text](https://github.com/ochik100/TraveLearn/blob/master/graph/images/pipeline.png)
