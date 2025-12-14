def read_instance(filename):
    with open(filename, "r") as f:
        data = f.readlines()
 
    data = [line.strip() for line in data]
 
    #  First line
    V, E, R, C, X = map(int, data[0].split())
 
    # 2. Video sizes
    video_size = list(map(int, data[1].split()))
 

    # 3. Endpoints
    idx = 2
    LD = []                    # datacenter latency
    connections = []           # list of dicts: { cache_id : latency }
    for e in range(E):
        ld, K = map(int, data[idx].split())
        idx += 1
        LD.append(ld)
        con = {}
        for _ in range(K):
            c, lc = map(int, data[idx].split())
            con[c] = lc
            idx += 1
        connections.append(con)
 

    # 4. Requests
    requests = []       # list of tuples (video, endpoint, n_requests)
    for r in range(R):
        v, e, n = map(int, data[idx].split())
        requests.append((v, e, n))
        idx += 1
 
    return V, E, R, C, X, video_size, LD, connections, requests
 
 
# EXAMPLE USAGE
if __name__ == "__main__":
    instance = read_instance("trending_4000_10K.in")
    print("Instance loaded successfully!")
    print(instance)
 