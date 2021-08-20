#include "server.h"
#include <vector>
#include <chrono>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include<fstream>

using namespace std;
using namespace std::chrono;
struct mythread *setUpThreads(struct config *);
void setUpThreads2( vector<struct mythread *>& ,struct config *);
extern void *serverthread(void *);
extern int init_thread(struct mythread *, int);
#define PERFROMANCE 0
int parse_config(const char *filename, struct config *conf)
{
    FILE *f = fopen(filename, "r");
    if (f == NULL)
    {
        printf("Couldn't open file at %s\n", filename);
        return -1;
    }
    if (fscanf(f, "%s\n", (conf->ipv4_addr)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%s\n", (conf->port)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->backlog)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->threadpoolsize)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->poolwindownsize)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->maxevents)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%f\n", &(conf->load)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->max_recv_conn)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->hop)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    if (fscanf(f, "%d\n", &(conf->cache_size)) != 1)
    {
        printf("wrong input file format\n");
        return -1;
    };
    conf->total_max_active = conf->threadpoolsize * conf->maxevents;    
    // conf->thPoolIdx = -1;
    // printf("IPV4 : %s\nport: %s\nthreadpoolsize : %d\n", conf->ipv4_addr, conf->port, conf->threadpoolsize);
    
    return 0;
}
int inc_index(int curr,int max){
    int new_idx = (curr + 1)% (max+1);
    new_idx = (new_idx == 0 ? 1 : new_idx);
    return new_idx;
}
vector<struct mythread *> curr_tpool;
pthread_mutex_t main_lock;
int total_active_connection = 0;
int performance = PERFROMANCE;
int total_recvd_connection = 0;
auto start = high_resolution_clock::now();
auto stop = high_resolution_clock::now();


struct config *conf;
int main()
{
    printf("[pid] : %d\n",getpid());
    pthread_mutex_init( &(main_lock),NULL);
    conf = new struct config;
    const char *inputFileName = "./config.txt";
    if (parse_config(inputFileName, conf))
    {
        perror("parsing error\n");
    }

    /* -------------------------Server Setup-----------------------*/
    struct addrinfo hints, *result, *p;
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    int s = getaddrinfo(conf->ipv4_addr, conf->port, &hints, &result);

    if (s != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        exit(1);
    }
    int listener = -1;
    int optval = 1;
    for (p = result; p != NULL; p = p->ai_next)
    {
        if ((listener = socket(p->ai_family, p->ai_socktype,
                               p->ai_protocol)) == -1)
        {
            perror("server: socket");
            continue;
        }

        if (setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &optval,
                       sizeof(int)) == -1)
        {
            perror("setsockopt");
            exit(1);
        }

        if (bind(listener, p->ai_addr, p->ai_addrlen) == -1)
        {
            close(listener);
            perror("server: bind");
            continue;
        }

        break;
    }

    freeaddrinfo(result);
    if (p == NULL)
    {
        fprintf(stderr, "server: failed to bind\n");
        exit(1);
    }
    if (listen(listener, conf->backlog) != 0)
    {
        perror("listen()");
        exit(1);
    }
    printf("Waiting for connection...\n");
    /* -------------------------Server Setup-----------------------*/

    // struct mythread *curr_tpool = setUpThreads(conf);

    fstream file;
    if(performance == 1){
        file.open(("time_log.txt"),ios::app);
    }
    
    init_sync();
    setUpThreads2(curr_tpool,conf);
    curr_tpool[0]->context->ev->events = EPOLLIN;
    curr_tpool[0]->context->ev->data.fd = listener;
    if (epoll_ctl(curr_tpool[0]->context->epollfd, EPOLL_CTL_ADD, listener, curr_tpool[0]->context->ev) == -1)
    {
        perror("epoll_ctrl error\n");
    }
    curr_tpool[0]->context->ev->data.fd = 0;
    if (epoll_ctl(curr_tpool[0]->context->epollfd, EPOLL_CTL_ADD, 0, curr_tpool[0]->context->ev) == -1)
    {
        perror("stdin : epoll_ctrl error\n");
    }    
    int nfds = 0;
    socklen_t addrlen;
    struct sockaddr_storage client_saddr;
    char str[INET6_ADDRSTRLEN];
    struct sockaddr_in *ptr;

    int CurrThreadindex = 1;
    int server_Status = 1;
    while (server_Status)
    {
        if(performance ==1 && total_recvd_connection == conf->max_recv_conn){
            stop = high_resolution_clock::now();
            auto duration1 = duration_cast<microseconds>(stop - start);
            cout << "Time taken for receive:" << duration1.count() << " microseconds" << endl;
            while(total_active_connection !=0);
            stop = high_resolution_clock::now();
            auto duration = duration_cast<microseconds>(stop - start);
            cout << "Time taken for service:" << duration.count() << " microseconds" << endl;
            file << (1000000 * total_recvd_connection)/duration1.count()<<" "<< (1000000 * total_recvd_connection)/duration.count()<<endl;
            total_recvd_connection = 0;
            conf->max_recv_conn += conf->hop;

        }
        if ((nfds = epoll_wait(curr_tpool[0]->context->epollfd, curr_tpool[0]->context->ep_events, curr_tpool[0]->context->maxevents, -1)) == -1)
        {
            perror("main epoll_wait\n");
        }
        if(performance ==1 && total_recvd_connection == 0 && total_active_connection ==0){
            start = high_resolution_clock::now();
        }
        for(int i=0;i<nfds;i++){
            if ((curr_tpool[0]->context->ep_events[i].events & EPOLLIN) == EPOLLIN){
                if (curr_tpool[0]->context->ep_events[i].data.fd == listener){
                    // new connection
                    // printf("got connection request\n");
                    addrlen = sizeof(struct sockaddr_storage);
                    int fd_new;
                    if( (fd_new = accept(listener,(struct sockaddr *)&client_saddr,&addrlen))== -1  ){
                        perror("accept\n");
                    }
                    // printf("connection accepted\n");
                    // find the proper index

                    // need synhronization
                    while(1){
                        pthread_mutex_lock(& (curr_tpool[CurrThreadindex]->lock));
                        int actv_clinet_th = curr_tpool[CurrThreadindex]->context->activeClints;
                        if(actv_clinet_th == curr_tpool[CurrThreadindex]->context->maxevents){
                            pthread_mutex_unlock(& (curr_tpool[CurrThreadindex]->lock));
                            // check if new thread is required
                            int tot_ac_conn=0;
                            // lock
                            pthread_mutex_lock(&main_lock);
                            tot_ac_conn = total_active_connection;
                            pthread_mutex_unlock(&main_lock);
                            // unlock
                            if(tot_ac_conn >= (int)((conf->load)*(conf->total_max_active))  ){
                                int lastidx = conf->threadpoolsize;
                                for(int j=0;j<conf->poolwindownsize;j++){
                                    struct mythread *thread = new struct mythread();
                                    curr_tpool.push_back(thread);
                                    conf->threadpoolsize++;
                                    init_thread(curr_tpool[conf->threadpoolsize], conf->maxevents);
                                    // printf("new thread: epollfd : %d\tmaxevents : %d\n", curr_tpool[conf->threadpoolsize]->context->epollfd, curr_tpool[conf->threadpoolsize]->context->maxevents);
                                    pthread_create(&(curr_tpool[conf->threadpoolsize]->tid), NULL, serverthread, (void *)curr_tpool[conf->threadpoolsize]);
                                }

                                conf->total_max_active = conf->threadpoolsize * conf->maxevents;
                                CurrThreadindex = lastidx;
                                // printf("new CurrentTHread index : %d\n",CurrThreadindex);
                            }

                            CurrThreadindex = inc_index(CurrThreadindex,conf->threadpoolsize);
                            continue;
                        }
                        curr_tpool[CurrThreadindex]->context->activeClints++;
                        pthread_mutex_unlock(& (curr_tpool[CurrThreadindex]->lock));
                        //lock
                        pthread_mutex_lock(&main_lock);
                        total_active_connection++;
                        total_recvd_connection++;
                        pthread_mutex_unlock(&main_lock);
                        // unlock
                        break;
                    }
                    curr_tpool[CurrThreadindex]->context->ev->events = EPOLLIN;
                    curr_tpool[CurrThreadindex]->context->ev->data.fd= fd_new;
                    if(epoll_ctl( curr_tpool[CurrThreadindex]->context->epollfd,EPOLL_CTL_ADD,fd_new,curr_tpool[CurrThreadindex]->context->ev) == -1){
                        perror("epoll ctrl\n");
                    }
                    // printf("connection added to worker thread no : %d\n",CurrThreadindex);
       
                    
                }else{
                    // printf("hello");
                    char *buff = new char[1024];
                    int len = read(0,buff,1024);
                    // buff[len-1] = '\0';
                    // printf("len :%d\n",len);
                    if(strncmp(buff,"exit",4) == 0){
                        delete []buff;
                        server_Status = 0;
                    }else{
                        printf("%s",buff);
                        delete []buff;
                    }
                    
                }
            }
        }
        CurrThreadindex = (CurrThreadindex + 1) % (conf->threadpoolsize + 1);
        CurrThreadindex = (CurrThreadindex == 0 ? 1 : CurrThreadindex);
    }
    if(server_Status == 0){
        while(1){
            int ac_conn = -1;
            pthread_mutex_lock(&main_lock);
            ac_conn = total_active_connection;
            pthread_mutex_unlock(&main_lock);
            if(ac_conn == 0){
                break;
            }
        }

        for (int i = 1; i < conf->threadpoolsize + 1; i++)
        {
            delete curr_tpool[i]->context->ev;
            delete []curr_tpool[i]->context->ep_events;
            delete curr_tpool[i]->context;
        }        
        exit(0);
    }

    for (int i = 1; i < conf->threadpoolsize + 1; i++)
    {
        pthread_join(curr_tpool[i]->tid, NULL);
    }
    return 0;
}
struct mythread *setUpThreads(struct config *conf)
{

    struct mythread *threadpool;
    threadpool = new struct mythread[conf->threadpoolsize];
    threadpool[0].tid = pthread_self();
    init_thread(&threadpool[0], 1);

    for (int i = 1; i < conf->threadpoolsize + 1; i++)
    {
        init_thread(&threadpool[i], conf->maxevents);
        pthread_create(&(threadpool[i].tid), NULL, serverthread, (void *)&threadpool[i]);
    }
    return threadpool;
}

// struct mythread **setUpThread1(struct config *conf)
// {

//     conf->thPoolIdx++;
//     struct mythread **threadpool = new struct mythread *[1000];
//     threadpool[conf->thPoolIdx] = new struct mythread[conf->threadpoolsize];
//     threadpool[conf->thPoolIdx][0].tid = pthread_self();
//     init_thread(&threadpool[conf->thPoolIdx][0], 1);

//     for (int i = 1; i < conf->threadpoolsize + 1; i++)
//     {
//         init_thread(&threadpool[conf->thPoolIdx][i], conf->maxevents);
//         pthread_create(&(threadpool[conf->thPoolIdx][i].tid), NULL, serverthread, (void *)&threadpool[conf->thPoolIdx][i]);
//     }
//     return threadpool;
// }
void setUpThreads2( vector<struct mythread *>& threadpool,struct config *conf)
{
    struct mythread *thread = new struct mythread();
    threadpool.push_back(thread);
    threadpool[0]->tid = pthread_self();
    init_thread(threadpool[0], 2);

    for (int i = 1; i < conf->threadpoolsize + 1; i++)
    {
        thread = new struct mythread();
        threadpool.push_back(thread);
        init_thread(threadpool[i], conf->maxevents);
        // printf("main : epollfd : %d\tmaxevents : %d\n", threadpool[i]->context->epollfd, threadpool[i]->context->maxevents);
        pthread_create(&(threadpool[i]->tid), NULL, serverthread, (void *)threadpool[i]);
    }
    return;
}
