# PiLet \
##Function deployment: \
`<faas-cli publish -f yolo3.yml --platforms linux/amd64,linux/arm64,linux/arm/v7>` \
`<faas-cli deploy -f yolo3.yml>` 

##Run load_generator.py \
`<python3 load_generator.py>` 

##What does it do?
It is a Flask server that (1) executes `<generator>` method to create and send async http requests (+ an image) to the function `<yolo3>'. \
When the task is done by `<yolo3>` function, (2) it returns back the response to the route `<actuator>` in the Flask server. \
(3) The `<actuator>` measures the admission time (to openfaas gateway), execution time and round trip for each request. \
(4) An average of results is printed. 

##The problem!
a) It sometimes takes time to submit a task to Openfaas gateway, e.g., seconds. The `<admission time>` can show this. \
b) The `<X-Duration-Seconds>` value in the response header does not match the `<Exec-Time>` which gets the start time and end of the function execution. \
c) The round trip is sometimes much more than the sum of admission and execution durations. I am curious where the request is staying in that period?
