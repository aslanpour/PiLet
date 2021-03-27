from flask import Flask, request, send_file, make_response #pip3 install flask
from waitress import serve #pip3 install waitress
import requests
import threading
import datetime
import time

app = Flask(__name__)
app.config["DEBUG"] = True

#config
file_name = "./soccer.jpeg"
host_IP="10.76.7.92"
gateway_IP="10.76.7.91"
iterations=1
intervals=1
#end

requests_sent = 0
requests_recv = 0
request_log = {}
lock = threading.Lock()



def generator():
    global iterations
    global intervals
    global requests_sent
    
    #Iterations
    for i in range(iterations):        
        requests_sent +=1
        thread = threading.Thread(target= send_request, args=(requests_sent,))
        thread.start()
            
        time.sleep(intervals)
        
    return 'Success'


def send_request(counter):
    global file_name
    global host_IP
    global gateway_IP
    global request_log
    
    #create a request to function
    try:
        start = datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()        
        
        file={'image_file': open(file_name, 'rb')}
    
        #create request id
        index= str(start) + '-#' + str(counter)

        #request_log:
        #[0] start time
        #[1] admission duration (time taken to submit to gateway)
        #[2] finished time (returned time)
        #[3] execution duration (by openfaas)
        #[4] execution duration (actual time)
        #[5] round trip
        request_log[index]= [start, -1, -1, -1, -1, -1]
             
        ##E.g.: "curl -X POST -F image_file=@./soccer.jpeg -H "X-Callback-Url: http://10.76.7.91:5000/actuator" http://10.76.7.91:31112/async-function/yolo3"
                                               
        url = 'http://' + gateway_IP + ':31112/async-function/yolo3' 
        img = file
        header = {'X-Callback-Url':'http://' + host_IP + ':5000/actuator',
                  'Sensor-ID': index}
        response=requests.post(url, headers=header, files=img)
            
                                         
        if response.status_code==202 or response.status_code==200:
            now= datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
            elapsed = now - start
            
            #Set admission duration
            request_log[index][1]= elapsed
        else:
            print('Failed')
                    
    except requests.exceptions.RequestException as e:
        print(e)
        
        


@app.route('/actuator', methods=['POST'])
def actuator():
    global requests_recv
    global request_log

    with lock:
        now= datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
         
        requests_recv+=1
        
        #get request index
        index = str(request.headers.get('Sensor-Id'))
        print(str(request.headers))
        # Set request logs
        #[0]start time already set     
        #[1]admission duration already set
        #[2] finished time (returned time)
        request_log[index][2]= now
        #[3] execution duration (by openfaas)
        request_log[index][3]= float(request.headers.get('X-Duration-Seconds'))
        #[4] execution duration (actual time)
        request_log[index][4]= float(request.headers.get('Exec-Time2'))
        #[5] round trip
        request_log[index][5]=now - request_log[index][0]
        
    #termination check
    if requests_recv >=(iterations): 
        #all received
        
        #collect response times
        admission_time=[]
        execution_duration_openfaas=[]
        execution_duration_custom=[]
        round_trip=[]
        
        for item in request_log.values():
            admission_time.append(item[1])
            execution_duration_openfaas.append(item[3])
            execution_duration_custom.append(item[4])
            round_trip.append(item[5])
            
        #print results
        print('Avg. Admission time: ' + str(round(sum(admission_time)/len(admission_time),2)))
        print('Avg. Exec. Time (openfaas): ' + str(round(sum(execution_duration_openfaas)/len(execution_duration_openfaas),2)))
        print('Avg. Exec. Time (custom): ' + str(round(sum(execution_duration_custom)/len(execution_duration_custom),2)))
        print('Avg. Round Trip: ' + str(round(sum(round_trip)/len(round_trip),2)))

    return 'Success'


if __name__ == "__main__":
    
    generator()
    serve(app, host= '0.0.0.0', port='5000')