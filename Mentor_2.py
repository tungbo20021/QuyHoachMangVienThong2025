import math
import csv
import Node
import MENTOR
import networkx as nx
import matplotlib.pyplot as plt

def prim_dijkstra_backbone_links(ListPosition, backbone_nodes,ListMentor,center_node,alpha,MAX):
    import heapq

    print("=== BẮT ĐẦU THUẬT TOÁN PRIM-DIJKSTRA ===")
    node_map = {n.get_name(): n for n in ListPosition}
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 1. Tạo đồ thị gốc đầy đủ (G_full)
    G_full = nx.Graph()
    for i in range(len(ListPosition)):
        for j in range(i + 1, len(ListPosition)):
            n1, n2 = ListPosition[i], ListPosition[j]
            cost = math.sqrt((n1.get_position_x() - n2.get_position_x())**2 +
                             (n1.get_position_y() - n2.get_position_y())**2)
            G_full.add_edge(n1.get_name(), n2.get_name(), weight=cost)


    root = center_node.get_name()
    print(f"Khởi tạo gốc: {root}")
    in_tree = set([root])
    tree_edges = []

    # Tính Dijkstra từ gốc
    dijkstra_lengths = nx.single_source_dijkstra_path_length(G_full, root, weight='weight')

    # Heap: (α * dist(root, u) + euclid(u, v), u, v)
    heap = []
    for u in in_tree:
        for v in backbone_names:
            if v in in_tree or u == v:
                continue
            euclid = math.sqrt((node_map[u].get_position_x() - node_map[v].get_position_x())**2 +
                               (node_map[u].get_position_y() - node_map[v].get_position_y())**2)
            cost = alpha * dijkstra_lengths.get(u, float('inf')) + euclid
            heapq.heappush(heap, (cost, u, v))
            print(f"Khởi tạo cạnh ({u}, {v}) với nhãn: {alpha}*{dijkstra_lengths.get(u, float('inf')):.2f} + {euclid:.2f} = {cost:.2f}")

    while len(in_tree) < len(backbone_names):
        while True:
            cost, u, v = heapq.heappop(heap)
            if v not in in_tree:
                break
        print(f"Chọn cạnh ({u}, {v}) với nhãn {cost:.2f} để thêm vào cây.")
        tree_edges.append((u, v))
        in_tree.add(v)

        for w in backbone_names:
            if w in in_tree or w == v:
                continue
            euclid = math.sqrt((node_map[v].get_position_x() - node_map[w].get_position_x())**2 +
                               (node_map[v].get_position_y() - node_map[w].get_position_y())**2)
            d_v = nx.dijkstra_path_length(G_full, root, v, weight='weight')
            cost = alpha * d_v + euclid
            heapq.heappush(heap, (cost, v, w))
            print(f"  Cập nhật cạnh ({v}, {w}) với nhãn: {alpha}*{d_v:.2f} + {euclid:.2f} = {cost:.2f}")

    print("=== KẾT THÚC THUẬT TOÁN PRIM-DIJKSTRA ===")
    links = [(node_map[u], node_map[v]) for u, v in tree_edges]
    plot_backbone(ListPosition,ListMentor, links, MAX,None,None,None)

    return links


def Mentor2_ISP(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio,NumNode, Limit, umin, alpha, debug):
    # 1. Tính Mentor 1 để lấy các nhóm backbone và truy nhập
    ListMentor, ListBackbone,center_node, special_traffic, traffic_matrix  = MENTOR.MenTor([Node_copy(n) for n in ListPosition], TrafficMatrix, MAX, C, w, RadiusRatio,NumNode, Limit, debug)
    # 2. Lấy ra các backbone node (node đầu tiên mỗi group)
    backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 3. Xây dựng các liên kết backbone theo Prim-Dijkstra
    prim_links = prim_dijkstra_backbone_links(ListPosition, backbone_nodes, ListMentor, center_node, alpha, MAX)
    backbone_links = prim_links.copy()
    direct_links = []

    # Tạo đồ thị backbone từ các liên kết backbone
    backbone_graph = nx.Graph()
    for n1, n2 in backbone_links:
        backbone_graph.add_edge(n1.get_name(), n2.get_name())
    # 4. Tính toán các liên kết trực tiếp bổ sung
    hop_list = []
    node_map = {n.get_name(): n for n in ListPosition}
    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            try:
                hops = nx.shortest_path_length(backbone_graph, source=u, target=v)
                hop_list.append((u, v, hops, traffic))
            except nx.NetworkXNoPath:
                print(f"Không tồn tại đường đi từ {u} đến {v} trên backbone.")

    # Sắp xếp theo số hops giảm dần
    hop_list.sort(key=lambda x: x[2], reverse=True)
    final_hop_list = []
    term_hop_list = []
    # In ra kết quả đã sắp xếp
    for u, v, hops, traffic in hop_list:
        print(f"Cặp backbone {u} - {v}: số hops = {hops}, traffic = {traffic_matrix.at[u,v]}")
        
    print("------------------------------------------")

    # Xử lý ban đầu với hop_list
    for u, v, hops, traffic in hop_list:
        n = math.ceil(traffic_matrix.at[u, v] / C)
        u_compare = traffic_matrix.at[u, v] / (n * C)
        u_compare = round(u_compare, 2)
        print(f"Cặp backbone {u} - {v}: traffic = {traffic_matrix.at[u, v]}")
        print(f"n = upperbound(T({u},{v})/C)=upperbound({traffic_matrix.at[u,v]}/{C})={n}")
        print(f"u= T({u},{v})/(n*C)={traffic_matrix.at[u,v]}/({n}*{C}) ={u_compare:.2f}")
        if u_compare > umin:
            print("u > umin")
            if hops > 1:
                print(f"Thêm liên kết trực tiếp {u} - {v}")
                direct_links.append((u, v))
            else:
                print("Kết nối trực tiếp => thêm lưu lượng vào ({u},{v})")\
                
            traffic_matrix.at[u, v] += traffic_matrix.at[u, v]
            final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        else:
            print("u <= umin")
            if hops == 1:
                print("Kết nối trực tiếp => thêm lưu lượng vào ({u},{v})")
                traffic_matrix.at[u, v] += traffic_matrix.at[u, v]
                print(f"T({u},{v})={traffic_matrix.at[u, v]}")
                final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            else:
                print(f"Chuyển lưu lượng 1 hop qua mạng")
                # path = nx.shortest_path(backbone_graph, source=u, target=v)
                # if len(path) >= 2:
                #     min_traffic = float('inf')
                #     home_node = None
                #     for i in range(1, len(path) - 1):
                #         home = path[i]
                #         # Tổng lưu lượng hiện tại trên hai đoạn
                #         dist_uhome = math.sqrt((node_map[u].get_position_x() - node_map[home].get_position_x())**2 +
                #         (node_map[u].get_position_y() - node_map[home].get_position_y())**2)
                #         dist_homev = math.sqrt((node_map[home].get_position_x() - node_map[v].get_position_x())**2 +
                #         (node_map[home].get_position_y() - node_map[v].get_position_y())**2)
                #         dist_sum = dist_uhome + dist_homev
                #         print(f"cost({u},{home}) + cost({home},{v}) = {dist_uhome:.2f} + {dist_homev:.2f} = {dist_sum:.2f}")
                #         if dist_sum < min_traffic:
                #             min_traffic = dist_sum
                #             home_node = home
                #     print(f"Nút home giữa {u} và {v} là {home_node}")
                    # Cộng thêm traffic mới vào hai đoạn
                    hops_uhome = nx.shortest_path_length(backbone_graph, source=u, target=home_node)
                    hops_homev = nx.shortest_path_length(backbone_graph, source=home_node, target=v)
                    traffic_sum_uhome = traffic_matrix.at[u, home_node] + traffic_matrix.at[u, v]
                    traffic_sum_homev = traffic_matrix.at[home_node, v] + traffic_matrix.at[u, v]
                    print(f"Lưu lượng sau cộng: ({u},{home_node})={traffic_matrix.at[u,home_node]}+{traffic_matrix.at[u,v]}={traffic_sum_uhome}, ({home_node},{v})={traffic_matrix.at[home_node,v]}+{traffic_matrix.at[u,v]}={traffic_sum_homev}")
                    traffic_matrix.at[u, home_node] += traffic_matrix.at[u, v]
                    traffic_matrix.at[home_node, v] += traffic_matrix.at[u, v]
                    print(f"Số hops từ {u} đến {home_node}: {hops_uhome}, từ {home_node} đến {v}: {hops_homev}")
                    
                    if hops_uhome == 1:
                        final_hop_list.append((u, home_node, traffic_matrix.at[u, home_node]))
                    else:
                        term_hop_list.append((u, home_node, hops_uhome, traffic_matrix.at[u, home_node]))

                    if hops_homev == 1:
                        final_hop_list.append((home_node, v, traffic_matrix.at[home_node, v]))
                    else:
                        term_hop_list.append((home_node, v,hop_list, traffic_matrix.at[home_node, v]))
        print("------------------------------------------")

    # Lặp lại với term_hop_list cho đến khi trống
    while term_hop_list:
        u, v, hops, traffic = term_hop_list.pop(0)
        n = math.ceil(traffic_matrix.at[u, v] / C)
        u_compare = traffic_matrix.at[u, v] / (n * C)
        u_compare = round(u_compare, 2)
        print(f"Cặp backbone {u} - {v}: traffic = {traffic_matrix.at[u, v]}")
        print(f"n = upperbound(T({u},{v})/C)=upperbound({traffic_matrix.at[u,v]}/{C})={n}")
        print(f"u= T({u},{v})/(n*C)={traffic_matrix.at[u,v]}/({n}*{C}) ={u_compare:.2f}")
        if u_compare > umin:
            print("u > umin")
            if hops > 1:
                print(f"Thêm liên kết trực tiếp {u} - {v}")
                direct_links.append((u, v))
            else:
                print("Kết nối trực tiếp => thêm lưu lượng vào ({u},{v})")
            
            traffic_matrix.at[u, v] += traffic_matrix.at[u, v]
            final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        else:
            print("u <= umin")
            if hops == 1:
                print("Kết nối trực tiếp => thêm lưu lượng vào ({u},{v})")
                traffic_matrix.at[u, v] += traffic_matrix.at[u, v]
                print(f"T({u},{v})={traffic_matrix.at[u, v]}")
                final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            else:
                print(f"Chuyển lưu lượng 1 hop qua mạng")
                path = nx.shortest_path(backbone_graph, source=u, target=v)
                if len(path) >= 2:
                    min_traffic = float('inf')
                    home_node = None
                    for i in range(1, len(path) - 1):
                        home = path[i]
                        traffic_uhome = get_special_traffic(u, home, special_traffic)
                        traffic_homev = get_special_traffic(home, v, special_traffic)
                        traffic_sum = traffic_uhome + traffic_homev
                        print(f"cost({u},{home}) + cost({home},{v}) = {traffic_uhome} + {traffic_homev} = {traffic_sum}")
                        if traffic_sum < min_traffic:
                            min_traffic = traffic_sum
                            home_node = home
                    print(f"Nút home giữa {u} và {v} là {home_node}")
                    # Cộng thêm traffic mới vào hai đoạn
                    hops_uhome = nx.shortest_path_length(backbone_graph, source=u, target=home_node)
                    hops_homev = nx.shortest_path_length(backbone_graph, source=home_node, target=v)
                    traffic_sum_uhome = traffic_matrix.at[u, home_node] + traffic_matrix.at[u, v]
                    traffic_sum_homev = traffic_matrix.at[home_node, v] + traffic_matrix.at[u, v]
                    print(f"Lưu lượng sau cộng: ({u},{home_node})={traffic_matrix.at[u,home_node]}+{traffic_matrix.at[u,v]}={traffic_sum_uhome}, ({home_node},{v})={traffic_matrix.at[home_node,v]}+{traffic_matrix.at[u,v]}={traffic_sum_homev}")
                    traffic_matrix.at[u, home_node] += traffic_matrix.at[u, v]
                    traffic_matrix.at[home_node, v] += traffic_matrix.at[u, v]
                    print(f"Số hops từ {u} đến {home_node}: {hops_uhome}, từ {home_node} đến {v}: {hops_homev}")

                    if hops_uhome == 1:
                        final_hop_list.append((u, home_node, traffic_matrix.at[u, home_node]))
                    else:
                        term_hop_list.append((u, home_node, hops_uhome, traffic_matrix.at[u, home_node]))

                    if hops_homev == 1:
                        final_hop_list.append((home_node, v, traffic_matrix.at[home_node, v]))
                    else:
                        term_hop_list.append((home_node, v, hops_homev, traffic_matrix.at[home_node, v]))
        print("------------------------------------------")
    print("Xét lưu lượng các kết nối 1 hop:")
    for u, v, traffic in final_hop_list:
       n = math.ceil(traffic_matrix.at[u, v] / C)
       print(f"Cặp backbone {u} - {v}: T({u},{v})={traffic_matrix.at[u, v]}, n = upperbound(T({u},{v})/C)=upperbound({traffic_matrix.at[u,v]}/{C})={n}") 
    plot_backbone(ListPosition, ListMentor, backbone_links, MAX, direct_links,True,final_hop_list)
    total_cost = 0
    total_cost_mentor = 0
    for n1, n2 in backbone_links:
        dx = n1.get_position_x() - n2.get_position_x()
        dy = n1.get_position_y() - n2.get_position_y()
        dist = math.sqrt(dx*dx + dy*dy)
        total_cost += dist
        print(f"Tổng cost Prim_Dijkstra (Tổng khoảng cách Euclid các liên kết backbone): {total_cost}")
    
    
    print("=== KẾT THÚC TÍNH TOÁN LIÊN KẾT TRỰC TIẾP ===")
    return backbone_names, ListMentor, prim_links, direct_links


def plot_backbone(ListPosition, _list_mentor, backbone_links, MAX, direct_links,done,final_hop_list):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'magenta', 'lime', 'brown']
    num_colors = len(colors)

    # Tạo node_map để tra cứu object Node từ tên node
    node_map = {n.get_name(): n for n in ListPosition}

    for group_idx, group in enumerate(_list_mentor):
        if not group:
            continue

        color = colors[group_idx % num_colors]

        xpos = []
        ypos = []

        for node in group:
            xpos.append(node.get_position_x())
            ypos.append(node.get_position_y())

        # --- Backbone Node ---
        backbone = group[0]
        plt.plot(backbone.get_position_x(), backbone.get_position_y(),
                 'o', markersize=14, markerfacecolor=color, markeredgecolor='black', markeredgewidth=2, zorder=3)
        plt.text(backbone.get_position_x(), backbone.get_position_y(), str(backbone.get_name()),
                 color='white', size=12, weight='bold', ha="center", va="center",
                 bbox=dict(facecolor=color, edgecolor='black', boxstyle='round'), zorder = 3)

        # --- Access Nodes ---
        for node in group[1:]:
            plt.plot(node.get_position_x(), node.get_position_y(),
                     'o', markersize=7, markerfacecolor=color, markeredgecolor='black', markeredgewidth=1, zorder = 2)
            plt.text(node.get_position_x(), node.get_position_y(), str(node.get_name()),
                     color='black', size=9, ha="center", va="center",
                     bbox=dict(facecolor=color, edgecolor='gray', boxstyle='round'), zorder = 2)

    # Vẽ liên kết backbone theo cây Prim-Dijkstra
    for n1, n2 in backbone_links:
        plt.plot([n1.get_position_x(), n2.get_position_x()],
                 [n1.get_position_y(), n2.get_position_y()], 'k-', linewidth=2, label='Backbone (Prim-Dijkstra)')

    # Vẽ các direct_links bằng đường đỏ
    if direct_links is not None:
        for n3, n4 in direct_links:
            node3 = node_map[n3] if n3 in node_map else n3
            node4 = node_map[n4] if n4 in node_map else n4
            plt.plot([node3.get_position_x(), node4.get_position_x()],
                     [node3.get_position_y(), node4.get_position_y()], color='red', linewidth=2, linestyle='--',label='Direct Link')
    if final_hop_list is not None:
            for u, v, traffic in final_hop_list:
                # Kiểm tra nếu (u, v) hoặc (v, u) không nằm trong direct_links
                if (u, v) not in direct_links and (v, u) not in direct_links:
                    node_u = node_map[u] if u in node_map else u
                    node_v = node_map[v] if v in node_map else v
                    plt.plot([node_u.get_position_x(), node_v.get_position_x()],
                             [node_u.get_position_y(), node_v.get_position_y()],
                             color='orange', linewidth=2,label='1-hop link')

    plt_margin = MAX * 0.05
    plt.axis([-plt_margin, MAX + plt_margin, -plt_margin, MAX + plt_margin])
    if done is None:
        plt.title("Cây Prim-Dijkstra các nút backbone", fontsize=14)
    else: 
        plt.title("Cây sau Mentor 1", fontsize=14)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

def Node_copy(node):
    # Deep copy cho Node tối giản
    n = Node.Node()
    n.create_name(node.get_name())
    n.set_position(node.get_position_x(), node.get_position_y())
    n.set_traffic(node.get_traffic())
    return n

def get_special_traffic(u, v, special_traffic):
    for uu, vv, traffic in special_traffic:
        if (uu == u and vv == v) or (uu == v and vv == u):
            return traffic
    return 0

