# XML_Warehouse

## Description
This project presents a warehousing tool for XML files. The first step of the project was to build an 'XML Diff and Patching Tool' that enabled me to find the diffs between XML versions as well as patch a version with changes to produce another version. The Warehouse offered several features such as Versioning, Temporal Querying, Query Subscription, Querying Changes, and the history of specific XML elements

## Tools
The project was developed using Python and the interface was built using PyQt5.   
For the backend, Firebase was used.  
* Firebase Authentication was used to manage users and their access to the warehouse. 
* Firebase Cloud Storage was used to store the latest XML files on the Cloud as well as the diffs between previous versions of XML files and the new versions. 
* Firebase Realtime Database was used to store relevant information about files, users, and more. 
