Config:

    source venv/bin/activate  
    pip3 install requests           # For query
    pip3 install prometheus_client  # For prometheus client.
    
To run a single query:

    python3 prometheus_querier.py
    > Total Downtime count:  2 
    > Average duration Seconds: 360.0      (or in minutes:  6.0 )

To run HTTP server that servers metric mtd_myapp_mean_time_to_recover (guague) on http://localhost:8080/metrics:

    python3 mtd_exporter.py 

To deploy on openshift:

    oc new-app python:3.6~https://github.com/LeoUfimtsev/mtd_parser
    oc start-build mtdparser --follow --wait --loglevel=4
    oc get logs

    # You might have to externalize the route manually. (or 'oc expose svc ....)
