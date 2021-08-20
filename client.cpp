#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include<iostream>
#include<cstring>
#include <unistd.h>
#include "KVClient.h"

using namespace std;

void error(char *msg)
{
    perror(msg);
    exit(0);
}

int main(int argc, char *argv[])
{
    int sockfd, portno, n;

    struct sockaddr_in serv_addr;
    struct hostent *server;

    char* buffer = new char[1024];
    if (argc < 3) {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    }
    portno = atoi(argv[2]);
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        perror("ERROR opening socket");
    server = gethostbyname(argv[1]);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }
    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
         (char *)&serv_addr.sin_addr.s_addr,
         server->h_length);
    serv_addr.sin_port = htons(portno);
    if (connect(sockfd,(struct sockaddr *)&serv_addr,sizeof(serv_addr)) < 0) 
        perror("ERROR connecting");
    while(1)
    {
        printf("Please enter the message: ");
        bzero(buffer,1025);
        fgets(buffer,1024,stdin);

        // printf("%s",buffer);

        char* encoded_request = encode_request(buffer);
        n = send(sockfd,encoded_request,MessageSize,0);
        if (n < 0) 
            break;
        bzero(buffer,MessageSize + 1);
        n = recv(sockfd,buffer,MessageSize,0);
        if (n < 0) 
            break;
        char* decoded_response = decode_response(buffer);
        printf("%s\n",decoded_response);

        delete[] encoded_request;
        delete[] decoded_response;
        // break;
    }
    return 0;
}
