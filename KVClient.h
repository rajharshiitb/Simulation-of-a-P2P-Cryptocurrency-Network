#define KeySize                 256
#define ValueSize               256
#define StatusSize              1
#define MessageSize             KeySize + ValueSize + StatusSize
#define ServerResponseMessage   25
#define UserStatusCode          10


char* encode_request(char* client_request);
char* decode_response(char* client_request);