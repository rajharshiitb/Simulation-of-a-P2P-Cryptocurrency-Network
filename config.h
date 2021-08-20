struct config
{
    char ipv4_addr[16];
    char port[6];
    int backlog;
    int threadpoolsize;
    int maxevents;
    // int thPoolIdx;
    int total_max_active;
    float load;
    int poolwindownsize;
    int max_recv_conn;
    int hop;
    int cache_size;
};