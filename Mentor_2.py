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
    plot_backbone(ListPosition,ListMentor, links, MAX)

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
    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            try:
                hops = nx.shortest_path_length(backbone_graph, source=u, target=v)
                hop_list.append((u, v, hops, traffic))
            except nx.NetworkXNoPath:
                print(f"Không tồn tại đường đi từ {u} đến {v} trên backbone.")

    # Sắp xếp theo số hops giảm dần
    hop_list.sort(key=lambda x: x[2], reverse=True)

    # In ra kết quả đã sắp xếp
    for u, v, hops, traffic in hop_list:
        print(f"Cặp backbone {u} - {v}: số hops = {hops}, traffic = {traffic_matrix.at[u,v]}")

    print("------------------------------------------")

    for u, v, hops, traffic in hop_list:
        n = math.ceil(traffic_matrix.at[u, v] / C)
        u_compare = traffic_matrix.at[u, v] / (n * C)
        u_compare = round(u_compare, 2)
        print(f"Cặp backbone {u} - {v}: n = upperbound(T({u},{v})/{C})={n}, u= T({u},{v})/({n}*{C})= {u_compare:.2f}")
        if u_compare > umin:
            print("u > umin")
            print(f"Thêm liên kết trực tiếp {u} - {v}")
            node_map = {n.get_name(): n for n in ListPosition}
            direct_links.append((node_map[u], node_map[v]))
        else:
            print("u<=umin")
            if hops == 1:
                print(f"Cặp này chỉ 1 hop, không thêm liên kết trực tiếp. Lưu lượng hiện tại: {traffic_matrix.at[u, v]}")
                # Không thêm direct_links, chỉ hiển thị lưu lượng
            else:
                print(f"Chuyển lưu lượng 1 hop qua mạng")
                path = nx.shortest_path(backbone_graph, source=u, target=v)
                if len(path) > 2:
                    min_traffic = float('inf')
                    home_node = None
                    for i in range(1, len(path) - 1):
                        home = path[i]
                        # Tổng lưu lượng hiện tại trên hai đoạn
                        traffic_sum = traffic_matrix.at[u, home] + traffic_matrix.at[home, v]
                        if traffic_sum < min_traffic:
                            min_traffic = traffic_sum
                            home_node = home
                    print(f"Nút home giữa {u} và {v} là {home_node} (tổng lưu lượng hiện tại trên 2 đoạn = {min_traffic})")
                    # Cộng thêm traffic mới vào hai đoạn
                    traffic_matrix.at[u, home_node] += traffic_matrix.at[u, v]
                    traffic_matrix.at[home_node, v] += traffic_matrix.at[u, v]
                    print(f"Lưu lượng sau cộng: ({u},{home_node})={traffic_matrix.at[u, home_node]}, ({home_node},{v})={traffic_matrix.at[home_node, v]}")
                else:
                    print("Không tìm được nút home phù hợp (đường đi quá ngắn)")
            print("------------------------------------------")

    print("=== KẾT THÚC TÍNH TOÁN LIÊN KẾT TRỰC TIẾP ===")    
    return backbone_names, ListMentor, prim_links, direct_links


def plot_backbone(ListPosition,_list_mentor, backbone_links, MAX):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'magenta', 'lime', 'brown']
    num_colors = len(colors)

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

    # Thiết lập vùng hiển thị
    
    # Vẽ liên kết backbone theo cây Prim-Dijkstra
    for n1, n2 in backbone_links:
        plt.plot([n1.get_position_x(), n2.get_position_x()],
                 [n1.get_position_y(), n2.get_position_y()], 'k-', linewidth=2)
    plt_margin = MAX * 0.05
    plt.axis([-plt_margin, MAX + plt_margin, -plt_margin, MAX + plt_margin])
    plt.title("Cây Prim-Dijkstra các nút backbone", fontsize=14)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()

def plot_backbone_full(ListPosition, _list_mentor, prim_links, direct_links, MAX):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'magenta', 'lime', 'brown']
    num_colors = len(colors)

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
                 bbox=dict(facecolor=color, edgecolor='black', boxstyle='round'), zorder=3)

        # --- Access Nodes ---
        for node in group[1:]:
            plt.plot(node.get_position_x(), node.get_position_y(),
                     'o', markersize=7, markerfacecolor=color, markeredgecolor='black', markeredgewidth=1, zorder=2)
            plt.text(node.get_position_x(), node.get_position_y(), str(node.get_name()),
                     color='black', size=9, ha="center", va="center",
                     bbox=dict(facecolor=color, edgecolor='gray', boxstyle='round'), zorder=2)

    # Vẽ liên kết backbone cũ (Prim-Dijkstra) - màu đen
    for n1, n2 in prim_links:
        plt.plot([n1.get_position_x(), n2.get_position_x()],
                 [n1.get_position_y(), n2.get_position_y()], color='black', linewidth=2, linestyle='-')

    # Vẽ tất cả các liên kết trực tiếp bổ sung - màu đỏ
    for n1, n2 in direct_links:
        plt.plot([n1.get_position_x(), n2.get_position_x()],
                 [n1.get_position_y(), n2.get_position_y()], color='red', linewidth=3, linestyle='-')

    # Thêm chú thích
    if direct_links:
        plt.plot([], [], color='red', linewidth=3, linestyle='-', label='Liên kết trực tiếp bổ sung')
    if prim_links:
        plt.plot([], [], color='black', linewidth=2, linestyle='-', label='Prim-Dijkstra')

    plt.legend()
    plt_margin = MAX * 0.05
    plt.axis([-plt_margin, MAX + plt_margin, -plt_margin, MAX + plt_margin])
    plt.title("Các liên kết backbone (đen: Prim-Dijkstra, đỏ: trực tiếp bổ sung)", fontsize=14)
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
