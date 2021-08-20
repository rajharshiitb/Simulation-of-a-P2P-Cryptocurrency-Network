#include "server.h"

using namespace std;
void *serverthread(void *);
extern int total_active_connection;
extern pthread_mutex_t main_lock;
extern char* handle_specific_request(char* );
int init_thread(struct mythread *th, int maxevents)
{
    th->context = new struct context;
    if ((th->context->epollfd = epoll_create(1)) == -1)
    {
        perror("epoll create");
        exit(1);
    }
    pthread_mutex_init( &(th->lock),NULL);
    th->context->activeClints = 0;
    th->context->maxevents = maxevents;
    th->context->ev = new struct epoll_event;
    th->context->ep_events = new struct epoll_event[maxevents];
    // printf("context :epollfd : %d max:%d\n",th->context->epollfd,th->context->maxevents);    
    return 0;
}
int destroy_thread(struct mythread *th)
{
    delete th->context->ev;
    delete [] th->context->ep_events;
    delete th->context;
    return 0;
}
void *serverthread(void *arg)
{
    struct mythread thisthread = *((struct mythread *)arg);
    // printf("hello from %lu , printing my content:", thisthread.tid);
    // printf("epollfd : %d\tmaxevents : %d\n", thisthread.context->epollfd, thisthread.context->maxevents);
    int CurrThreadindex = 1;

    int nfds = 0;
    while (true)
    {
        if ((nfds = epoll_wait(thisthread.context->epollfd, thisthread.context->ep_events, thisthread.context->maxevents, -1)) == -1)
        {
            sleep(1);
            perror("serverthread:epoll_wait\n");
        }
        for(int i=0;i<nfds;i++){
            if ((thisthread.context->ep_events[i].events & EPOLLIN) == EPOLLIN){         // data is ready for read     
                char *recv_message = new char[1024];
                memset(recv_message,'\0',sizeof(recv_message));
                // printf("before recv call\n");
                ssize_t numofbytes = recv(thisthread.context->ep_events[i].data.fd,recv_message,1024,0);
                recv_message[numofbytes] = '\0';
                // printf("after recv call : %ld\n",numofbytes);
                if(numofbytes == -1){
                    perror("recv error\n");
                }
                else if(numofbytes == 0){ // close connection
                    // // synchronization needed
                    pthread_mutex_lock(& (thisthread.lock));
                    thisthread.context->activeClints--;
                    pthread_mutex_unlock(& (thisthread.lock));
                    pthread_mutex_lock(&main_lock);
                    total_active_connection--;
                    pthread_mutex_unlock(&main_lock);
                    // printf("closing connection\n");
                    if(epoll_ctl(thisthread.context->epollfd,EPOLL_CTL_DEL,thisthread.context->ep_events[i].data.fd,thisthread.context->ev)  == -1){
                        perror("cpoll ctl error\n");
                    }
                    if( close(thisthread.context->ep_events[i].data.fd) == -1){
                        perror("close error\n");
                    }
                }
                else{ // actual data from client
                    // printf("received %s in worker thread %ld\n",recv_message,thisthread.tid);
                    // processing happens here
                    char *send_message;
                    send_message = handle_specific_request(recv_message);
                    
                    // sprintf(send_message,"%s",send_message);
                    // printf("Sending %s of length %ld\n",send_message,strlen(send_message));
                    if(send(thisthread.context->ep_events[i].data.fd,send_message,strlen(send_message),0)== -1){
                        perror("send error\n");
                    }
                    delete[] send_message;

                }
                delete[] recv_message;
            }
        }
    }
}