def read_instance(filename):
    """
    Parses a caching problem instance file and returns the system parameters.
    """
    with open(filename, "r") as f:
        data = f.readlines()

    # Remove leading/trailing whitespace from every line
    data = [line.strip() for line in data]

    # Set initial index for reading data lines
    idx = 0 
    
    # -----------------------------
    # 1. First line: Global Parameters
    # -----------------------------
    # V: Videos, E: Endpoints, R: Requests, C: Caches, X: Cache Capacity
    V, E, R, C, X = map(int, data[idx].split())
    idx += 1

    # -----------------------------
    # 2. Video sizes
    # -----------------------------
    video_size = list(map(int, data[idx].split()))
    idx += 1

    # -----------------------------
    # 3. Endpoints and Cache Connections
    # -----------------------------
    LD = []                     # Datacenter latency
    connections = []            # list of dicts: { cache_id : latency_to_cache }
    for e in range(E):
        # Read datacenter latency (ld) and number of connected caches (K)
        ld, K = map(int, data[idx].split())
        idx += 1
        LD.append(ld)
        
        con = {}
        for _ in range(K):
            # Read cache ID (c) and latency to cache (lc)
            c, lc = map(int, data[idx].split())
            con[c] = lc
            idx += 1
        connections.append(con)

    # -----------------------------
    # 4. Requests
    # -----------------------------
    requests = []       # list of tuples (video, endpoint, n_requests)
    for r in range(R):
        v, e, n = map(int, data[idx].split())
        requests.append((v, e, n))
        idx += 1

    # Final return of all parsed data
    return V, E, R, C, X, video_size, LD, connections, requests

# EXAMPLE USAGE
if __name__ == "__main__":
    # Note: Ensure 'trending_4000_10K.in' exists in the same directory
    try:
        instance = read_instance("trending_4000_10K.in")
        print("Instance loaded successfully!")
        # Print a summary instead of the entire (potentially large) instance data
        V, E, R, C, X, video_size, LD, connections, requests = instance
        print(f"Summary: {V} Videos, {E} Endpoints, {C} Caches (Capacity {X}), {len(requests)} Request Descriptions.")
    except FileNotFoundError:
        print("Error: The file 'trending_4000_10K.in' was not found.")