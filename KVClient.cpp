#include<iostream>
#include<string.h>
#include "KVClient.h"

using namespace std;



char *string_tok(char *rem, char delim, char **remaining)       /*function for tokenization of string*/
{
    char *temp = rem;
    while (*temp != '\0' && *temp != delim && *temp != '\n')
        temp = temp + 1;
    
    while (*temp == delim || *temp == '\n')
    {
        *temp = '\0';
        temp = temp + 1;
    }
    *remaining = temp;
    if (strlen(rem) == 0)
        return NULL;
    return rem;
}

int _find_val_in_integer(char byte)
{
    /*this function finds the integer value of a sequnce of bytes*/
    int val = 0;
    for(int i = 0; i <= 7; i++)
    {
        if(((1 << i) & byte) != 0)
        {
            val = val + (1 << i);
        }
    }
    return val;
}

char* _form_message(char status_code, char* client_request)
{   
    // printf("%c",status_code);
    char* rest = client_request;
    char* key = string_tok(rest,' ',&rest);
    char* value = NULL;
    if(status_code == '2')
        value = string_tok(rest,' ',&rest);
    char _padded_key[KeySize], _padded_value[ValueSize];
    char* _formed_message = new char[MessageSize];

    if(value != NULL && (strlen(key) > KeySize || strlen(value) > ValueSize))
    {
        printf("Key or value size is out of bound");
        exit(1);
    }

    memset(_padded_key, '~', KeySize);
    memset(_padded_value,'~', ValueSize);
    memset(_formed_message,'~',MessageSize);

    memcpy(_padded_key, key, strlen(key));
    if(value != NULL)
        memcpy(_padded_value,value,strlen(value));
    memcpy(_formed_message,&status_code,StatusSize);
    memcpy(_formed_message + StatusSize, _padded_key,KeySize);
    memcpy(_formed_message + StatusSize + KeySize, _padded_value, ValueSize);
    if(*rest != '\0')
        return NULL;
    return (char*)_formed_message;
}

char* encode_request(char* client_request)
{
    char *rest = client_request;

    char* status_code = string_tok(rest,' ',&rest); 
    char* formated_message = NULL;
    if(strcmp(status_code, "GET") == 0)
        formated_message = _form_message('1', rest);
    else if(strcmp(status_code, "PUT") == 0)
        formated_message = _form_message('2',rest);
    else if(strcmp(status_code, "DEL") == 0)
        formated_message = _form_message('3', rest);
    
    return (char*)formated_message;
}

char* decode_response(char* server_response)          //status_code represent which request was made(get, put, or del)
{
    char first_byte = server_response[0];
    int first_byte_integer = _find_val_in_integer(first_byte);
    if(first_byte_integer == 200)
    {
        char* success_message = new char[ServerResponseMessage + ValueSize + 1];
        memset(success_message,' ',ServerResponseMessage);
        memcpy(success_message,"Operation - Success:",20);

        success_message[ServerResponseMessage + ValueSize] = '~';

        memcpy(success_message + ServerResponseMessage, server_response + StatusSize + KeySize, ValueSize);

        char*iterator = success_message + ServerResponseMessage;

        while(*iterator != '~')
        {
            iterator++;
        }
        *iterator = '\0';


        return success_message;
    }
    else if(first_byte_integer == 240)
    {
        char* error_message = new char[ServerResponseMessage + ValueSize + 1];

        memset(error_message,' ',ServerResponseMessage + ValueSize);

        error_message[ServerResponseMessage + ValueSize] = '~';

        memcpy(error_message,"Operation - Error:",18);
        
        /*there'll be an error message in the value part of the message*/
        memcpy(error_message + ServerResponseMessage, server_response + StatusSize + KeySize, ValueSize);

        char*iterator = error_message + ServerResponseMessage;

        while(*iterator != '~')
        {
            iterator++;
        }
        *iterator = '\0';

        return error_message;
    }
    return NULL;
}
