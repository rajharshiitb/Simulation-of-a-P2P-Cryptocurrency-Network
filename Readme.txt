# CS765 Systems : Assignment - IV

* Team Members:

    |  Roll No   |   CSE LDAP           |     Name             |
    |:-----------:|:-------------------:|:--------------------:|
    |  203050059  |  harshrajiitb	    |   Harsh Raj          |
    |  20305R005  |  arnabdas	        |   Arnab Das          |
    |  203050008  |  imsagartyagi       |   Sagar Tyagi        |




----------------------------------------------------------------------------------------------------------------------------------------------
* Disclaimer
    1. Follow exact command format for the given client
    2. Config.txt must be present in current directory.
----------------------------------------------------------------------------------------------------------------------------------------------
* Steps to run the client side of the program

1.  Compiler both client and server
        make all
2.  First compile the client using following syntax
        make client

3.  First compile the server using following syntax
        make server
    
4.  After compiling, run the client using:
        make runclient
        OR,
        ./client <ip> <port>
    
    (eg. by default it uses localhost with port 1234, change make if needed)

5. Command in given Client : 
        1 . "PUT<space><key><space><value>"
        2.  "GET<space><key>"
        3.  "DEL<space><key>"

6. Config.txt Strucuture:
    1. IP Address of Server
    2. Port of Server
    3. Listen Backlog
    4. Inital ThreadPool size
    5. Threadpool Size : Threadpoll increase size if needed
    6. Poolwindowsize : Maximum Number of connection each thread handels
    7. load factor : if total active connection >= (load) * Maximum Possible connection increase threadpool size by poolwindow size
    8. Performance Analysis purpose : intial connection number to compute throughput
    9. Performance Analyssi purpuse : increase in connection
    10.Cache Size

    (Note : 8 and 9 can be given 0 )

7. For Server
        make runserver
        (make sure config.txt is present in current directory)

8. For Load Test (Optional):
    we have given 3 bash files which check Performance
    Make sure each client only send one request for using these bash files.
    1. Test for PUT : loadtest.bash 
    2. Test for GET : read.bash
    3. Test for DEL : delete.bash

----------------------------------------------------------------------------------------------------------------------------------------------
Server : 
We have one main thread for connection handle, and a threadpool.
If at any point one thread is completely full it is assumed that there is contention
if there is contention we check if total active connection in whole server >= loadFactor * MaxConnection Possible
if so we increase out threadpool by some size which is given in config.txt

For Persistent Storage : we have a hash function which generates index from given key
it then stores that key into that file.more than one key can go into one file.
we are max allowing 20 files which can be increassed in KVServer.h . 
within each file no order is maintained and we perfrom linear scan for searching.

Cache :
There is LRU cache on top of persistent storage.Default Cache entry size = 8
Cache size can be changed in config.txt

----------------------------------------------------------------------------------------------------------------------------------------------

* Client

    1. We have used a '~' character to append in the key and value to make it 256 bytes each. Total message size will be 513 bytes (1 byte status_code + 256 byte key + 256 byte value)
    2. If running on a single system make sure that no two peers or seed are running in same directory otherwise Output files will conflict
    3. There will be 3 files in the client side:
    
    	a) client.cpp
    		
    		-- This is the main file where client will be sending the request to the server in the loop, using a specified syntax ( given in "step to run the program"), this file send the encoded
    		   message of size 513 bytes, it gets the encoded message from the library file KVClient.cpp. This file also recieves the message sent by the server in the buffer and then decode it 
    		   with the help of KVClient.cpp library file.

    	b) KVClient.cpp
    	
    		-- This file contains the two important function "encode_message" and "decode_message". "encode_message" function simply takes the buffer input and append the '~' character upto 256 
    		   bytes in both key and value and then append it, lastly a status code is also appended to make it 513 bytes input."decode_message" takes the response of the server and checks the 
    		   status code(1st byte) of the input, then returns the message accordingly for reporting success and error.
    	
    	c) KVClinet.h
    		
    		-- This file contains all the headers and the function prototype to link the files.
    	
