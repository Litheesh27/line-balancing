import math, ast
from collections import deque, defaultdict

def normalize_cell(v):
    if v is None: return ""
    v = str(v).strip()
    if v.startswith("[") and v.endswith("]"):
        try:
            p = ast.literal_eval(v)
            if isinstance(p, list) and p: return str(p[0]).strip().upper()
        except: pass
    return v.upper()

def run_line_balancing(df, output_rate):

    df = df[df["Task"].notna() & (df["Task"].astype(str).str.strip() != "")].reset_index(drop=True)
    tasks = [normalize_cell(t) for t in df["Task"]]
    times = df["Time (min)"].astype(float).tolist()

    preds = [[] if normalize_cell(p)=="" else
             [x for x in normalize_cell(p).replace(" ","").split(",") if x]
             for p in df["Predecessors"]]

    task_time = dict(zip(tasks, times))
    task_preds = dict(zip(tasks, map(set, preds)))

    total_time = sum(times)
    cycle_time = 60 / output_rate
    n = math.ceil(total_time / cycle_time)

    graph, indeg = defaultdict(list), {t:0 for t in tasks}
    for t, ps in task_preds.items():
        for p in ps: 
            graph[p].append(t)
            indeg[t]+=1

    q, order = deque([t for t in tasks if indeg[t]==0]), []
    
    while q:
        t = q.popleft(); order.append(t)
        for x in graph[t]:
            indeg[x]-=1
            if indeg[x]==0: q.append(x)

    def assign(k):
        st = {f"Station {i+1}":{"tasks":[],"time":0} for i in range(k)}
        indeg2 = {t:len(task_preds[t]) for t in order}
        q = deque([t for t in order if indeg2[t]==0])
        
        while q:
            t = q.popleft()
            feas = [s for s in st if st[s]["time"]+task_time[t]<=cycle_time] or st.keys()
            s = min(feas, key=lambda x: st[x]["time"])
            st[s]["tasks"].append(t); st[s]["time"]+=task_time[t]
            for x in graph[t]:
                indeg2[x]-=1
                if indeg2[x]==0: q.append(x)
        ct = max(s["time"] for s in st.values())
        return st, ct, 60/ct

    while True:
        stations, ct, rate = assign(n)
        if rate>=output_rate: break
        n+=1

    return stations, ct, rate, n
