#include<string>
#include<cstring>
#include<fstream>
#include <semaphore.h> 
#include <list> 
#include <iterator> 
#include <utility>
#include "server.h"

// #define MAX_SIZE 8
extern struct config *conf;
int MAX_SIZE = 8;
using namespace std;

class LRUCache {
    public:
    // cache of each file
    list<string> key_value_cache;
 
    // store references of key in cache
    unordered_map<string, pair<string, list<string>::iterator>> m;
    sem_t write_cache_mutex;
     sem_t read_cache_mutex;

    LRUCache(){
        sem_init(&write_cache_mutex,0,1);
        sem_init(&read_cache_mutex,0,1);
    }

    string find(string key){
        string result = "NOT FOUND";// Key_Value Not Found
        // not present in cache
        if (m.find(key) == m.end()) {
            // cache is full
            if (key_value_cache.size() == MAX_SIZE) {
                // delete least recently used element
                string last = key_value_cache.back();
 
                // Pops the last elmeent
                key_value_cache.pop_back();
 
                // Erase the last from map
                m.erase(last.substr(0,KeySize));
            }
        }
 
        // present in cache
        else{
            key_value_cache.erase(m[key].second);
            result = m[key].first;
            m.erase(key);
        }
        return result;
    }
    void put(string key, string value){
        string key_value = key+value;
        pair<string, list<string>::iterator> p;
        key_value_cache.push_front(key_value);
        p = make_pair(value, key_value_cache.begin());
        m[key] = p;
    }
    void remove(string key){
        if(m.find(key) != m.end()){
            key_value_cache.erase(m[key].second);
            m.erase(key);
        }
    }
    void lock(){
        sem_wait(&write_cache_mutex);
    }
    void unlock(){
        sem_post(&write_cache_mutex);
    }
    void read_lock(){
        sem_wait(&read_cache_mutex);
    }
    void read_unlock(){
        sem_post(&read_cache_mutex);
    }
};

class reader_writer{
    public:
        int num_readers;
        sem_t mutex;
    reader_writer() {
        num_readers = 0;
        sem_init(&mutex,0,1);
    }  
    void lock(sem_t *roomEmpty){
        sem_wait(&mutex);
        num_readers++;
        if(num_readers==1){
            sem_wait(roomEmpty);
        }
        sem_post(&mutex);
    } 
    void unlock(sem_t *roomEmpty){
        sem_wait(&mutex);
        num_readers--;
        if(num_readers==0){
            sem_post(roomEmpty);
        }
        sem_post(&mutex);
    }
};
reader_writer *reader_writer_sync;
sem_t *turnstile, *roomEmpty;
LRUCache *lruCache;
/*
init_sync(void)
initializes all the synchronization variables 
main thread in server should call this once
*/
void init_sync(){
    MAX_SIZE = conf->cache_size;
    reader_writer_sync = new reader_writer[MAX_FILES];
    turnstile = new sem_t[MAX_FILES];
    roomEmpty = new sem_t[MAX_FILES];
    lruCache = new LRUCache[MAX_FILES];
    for(int i=0;i<MAX_FILES;i++){
        sem_init(&turnstile[i],0,1);
        sem_init(&roomEmpty[i],0,1);
    }

}

/*
Uses djb2 hash function to map each string to a file and 
return mapped file number
*/
int get_file_num(string key){
    //djb2
    unsigned long hash = 5381;
    int c;
    for(int i=0;i<key.length();i++){
        c = key[i];
        hash = ((hash << 5) + hash) + c; // hash*33 +c
    }
    return hash % MAX_FILES;
}

/*
put_key_value_pair(string, string)
    Takes key and value strings as arguments
*/
int put_key_value_pair(string key, string value){
    unsigned int file_num = get_file_num(key);
    string file_path = "file" + to_string(file_num) + ".txt";
    string key_value = key + value;
    fstream file;
    int error = 0; //0 if no error, 1 if error

    sem_wait(&turnstile[file_num]);
    sem_wait(&roomEmpty[file_num]);

    //Critical Section Start Here
    try{
        file.open(const_cast<char*>(file_path.c_str()),ios::app);
        file<<key_value<<endl;
        lruCache[file_num].find(key);
        lruCache[file_num].put(key, value);
        file.close();
    }
    catch(...){
        error = 1;
    }
    //Critical Section End Here

    sem_post(&turnstile[file_num]);
    sem_post(&roomEmpty[file_num]);
    return error;
}
/*
get_value(string)
    Takes key string as argument
    return value associated with the key

    what if key queried not found?: Return "NO"
*/
string get_value(string key){

    unsigned int file_num = get_file_num(key);
    string file_path = "file" + to_string(file_num) + ".txt";
    string key_value;
    string fetched_key;
    fstream file;
    string result ="KEY NOT FOUND";
    string cache_result;

    sem_wait(&turnstile[file_num]);
    sem_post(&turnstile[file_num]);
    reader_writer_sync[file_num].lock(&roomEmpty[file_num]);

    //Critical Section Start
    //lock
    lruCache[file_num].read_lock();
    cache_result = lruCache[file_num].find(key);
    lruCache[file_num].read_unlock();
    //unlock
    if(cache_result == "NOT FOUND"){
        // cout << "hello"<<endl;
        file.open(const_cast<char*>(file_path.c_str()),ios::in);
        file.seekg(0,ios::beg);
        while(file){
            getline(file,key_value);
            fetched_key = key_value.substr(0,KeySize);

            // cout<<key_value.substr(KeySize,ValueSize)<<"\n";
            // cout<<key_value.substr(KeySize,ValueSize).length()<<"\n";

            if(fetched_key == key){
                result =  key_value.substr(KeySize,ValueSize);
                lruCache[file_num].lock();
                lruCache[file_num].put(key, result);
                lruCache[file_num].unlock();
                break;
            }
        }
        file.close();
    }
    else{
        result = cache_result;
        lruCache[file_num].lock();
        lruCache[file_num].put(key, result);
        lruCache[file_num].unlock();
    }
    //Critical Section End

    reader_writer_sync[file_num].unlock(&roomEmpty[file_num]);

    return result;
}
/*
remove_key(string)
    Takes key and value strings as arguments
    Deltes key and corresponding value in file.
    return nothing
    TODO: Needs better implementation
*/
int remove_key(string key){
    unsigned int file_num = get_file_num(key);
    string file_path = "file" + to_string(file_num) + ".txt";
    string temp_file_path = "temp" + to_string(file_num) + ".txt";
    fstream file;
    fstream outfile;
    string key_value, fetched_key;
    int error = 1;

    sem_wait(&turnstile[file_num]);
    sem_wait(&roomEmpty[file_num]);

    //Critical Section Start Here
    try{
        lruCache[file_num].remove(key);
        file.open(const_cast<char*>(file_path.c_str()),ios::in);
        outfile.open(const_cast<char*>(temp_file_path.c_str()),ios::app);
        while(getline(file,key_value)){
            fetched_key = key_value.substr(0,KeySize);
            if(fetched_key != key){
                outfile<<key_value<<endl;
            }
            else{
                error = 0;
            }
        }
        file.close();
        remove(const_cast<char*>(file_path.c_str()));
        int pointer = outfile.tellg();
        outfile.close();
        if(pointer == 0){
            remove(const_cast<char*>(temp_file_path.c_str()));
        }
        else{
            rename(const_cast<char*>(temp_file_path.c_str()),const_cast<char*>(file_path.c_str()));
    }
    
    }
    catch(...){
        error = 1;
    }
    //Critical Section End Here

    sem_post(&turnstile[file_num]);
    sem_post(&roomEmpty[file_num]);

    return error;
}

/*
On top functions
*/

struct result* get_request_result(char *k){
    struct result* ans = new struct result;
    string key(k);
    string value = get_value(key);
    //240: Error
    //200: Found
    if(value == "KEY NOT FOUND"){
        ans->status_code = 240;
        strcpy(ans->message, value.c_str());
        strcpy(ans->value, "240");
    }
    else{
        ans->status_code = 200;
        strcpy(ans->message, "KEY VALUE FOUND");
        strcpy(ans->value, value.c_str());
    }
    return ans;
}

struct result* put_request_result(char *k, char *v){

    struct result* ans = new struct result;
    string key(k);
    string value(v);
    int error = put_key_value_pair(key, value);
    if(error == 0){
        ans->status_code = 200;
        strcpy(ans->message,"SUCCESFULL");
        strcpy(ans->value, value.c_str());
    }
    else{
        ans->status_code = 240;
        strcpy(ans->message, "ERROR IN SAVING KEY VALUE");
        strcpy(ans->value, "240");
    }
    return ans;
}

struct result* del_request_result(char* k){
    struct result* ans = new struct result;
    string key(k);
    int error = remove_key(key);
    if(error == 0){
        ans->status_code = 200;
        strcpy(ans->message, "SUCCESFULL");
        strcpy(ans->value, "200");
    }
    else{
        ans->status_code = 240;
        strcpy(ans->message,  "ERROR IN DELETING KEY VALUE");
        strcpy(ans->value, "240");
    }
    return ans;
}
