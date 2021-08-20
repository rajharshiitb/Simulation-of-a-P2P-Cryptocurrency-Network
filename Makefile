all: server client

server: server.cpp serverthread.cpp KVServer.cpp cache.cpp mythread.h server.h KVServer.h config.h
	g++ -pthread -o server server.cpp serverthread.cpp KVServer.cpp cache.cpp

client: client.cpp KVClient.cpp KVClient.h
	g++ -o client client.cpp KVClient.cpp 

clean:
	$(RM) server
	$(RM) client
	$(RM) time_log.txt

runserver: server config.txt
	./server

runclient: client
	./client localhost 1234

runput: loadtest.bash
	./loadtest.bash

runget: read.bash
	./read.bash

rundel: delete.bash
	./delete.bash