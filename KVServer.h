#define KeySize                 256
#define ValueSize               256
#define StatusSize              1
#define MessageSize             KeySize + ValueSize + StatusSize

#define MAX_FILES               20


void init_sync();
struct result* del_request_result(char* k);
struct result* put_request_result(char *k, char *v);
struct result* get_request_result(char *k);


struct result{
    int status_code;
    char value[KeySize];
    char message[ValueSize];
};