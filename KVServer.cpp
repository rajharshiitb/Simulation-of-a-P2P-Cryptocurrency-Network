/* A simple server in the internet domain using TCP
   The port number is passed as an argument */
// #include <stdio.h>
#include <netinet/in.h>
// #include<cstring>
#include "server.h"

int sockfd,portno;
struct sockaddr_in serv_addr;
void error(char *msg)
{
    perror(msg);
    exit(1);
}
/*In every successfull operation return the key and value as it is, in case of unsuccessfull operation put error message in Value part. (and change status code obviously)*/

char* create_response_message(char* key, struct result* query_result)
{
    char* response_message = new char[MessageSize + 1];
    bzero(response_message,MessageSize + 1);
    *response_message = char(query_result ->status_code);   // setting the status code.
    memcpy(response_message + StatusSize,key,KeySize);      //key will be same.
    if(query_result ->status_code == 200)
    {
        /*In this case the last (ValueSize) bytes will contains value*/
        memcpy(response_message + StatusSize + KeySize,query_result ->value,ValueSize);
        return response_message;
    }
    else if(query_result ->status_code == 240)
    {
        /*In this case the last (ValueSize) bytes will contains Error message*/
        memcpy(response_message + StatusSize + KeySize, query_result ->message,ValueSize);
        return response_message;
    }
    return NULL;
}

char* _value(char* _buffer)
{
    char* value = new char[ValueSize+1];
    bzero(value,ValueSize+1);
    memcpy(value, _buffer + StatusSize + KeySize,ValueSize);
    return value;
}

char* _key(char* _buffer)
{
    char* key = new char[KeySize+1];
    bzero(key,KeySize+1);
    memcpy(key,_buffer + StatusSize,KeySize);
    return key;
}

char* handle_specific_request(char* buffer)
{
    char* value = NULL;
    char* key = NULL;
    struct result* query_result =NULL;
    switch (*buffer)
    {
    case '1':
        { /* GET  request*/
            key = _key(buffer);
            // printf("handle req get key: %s\n",key);
            query_result = get_request_result(key);

            char* get_response_message = create_response_message(key,query_result);
            // printf("response_message %s",get_response_message);
            delete query_result;
            delete[] key; /*after using the key and creating the message remember to deallocate the memory*/
            return get_response_message;
            break;
        }
    case '2':
        {
            /* PUT request*/
            key = _key(buffer);
            value = _value(buffer); 
            query_result = put_request_result(key, value);       //I will catch it here from the function implemented by harsh
            char* put_response_message = create_response_message(key,query_result);
            
            delete query_result;
            delete[] key;
            delete[] value;
            return put_response_message;
            break;
        }
    case '3':
        {
            /* DEL request*/
            key = _key(buffer);
            
            query_result = del_request_result(key);

            char* del_response_message = create_response_message(key,query_result);
                        
            delete query_result; 
            delete[] key;
            return del_response_message;
            break;
        }
    default:
        break;
    }
    return NULL;
}


