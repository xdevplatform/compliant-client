# Compliant-client

A set of examples Python scripts for the compliance endpoints. Scripts for:
  1) Creating a Job 
  2) Checking on Job status and retrieving Job details.
  3) Uploading a text file with Tweet IDs (one per line).
  4) Downloading results which consist of JSON results for each Tweet that has a Compliance results (e.g. has been deleted).
  
  
Also, the start of a simple command-line app that references a compliance_client class.

```
compliant-client.py
Usage:
    compliant-client --all --name <name> --ids-file <ids-file> --results-file <results-file>
    compliant-client --create --name <name>
    compliant-client --list (--name <name> | --id <id>)
    compliant-client --upload (--name <name> | --id <id>) --ids-file <ids-file>
    compliant-client --download (--name <name> | --id <id>) --results-file <results-file>
    compliant-client --help
    compliant-client --version
Options:
    -a --all
    -c --create
    -l --list
    -u --upload
    -d --download
    -n --name
    -i --id
    -f --ids-file
    -r --results-file
    -h --help
    -v --version
    
```    
