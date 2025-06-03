import math
import csv
import Node
import MENTOR
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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
    print("=========================================")
    links = [(node_map[u], node_map[v]) for u, v in tree_edges]
    # plot_backbone(ListPosition,ListMentor, links, MAX,None,None,None,None)
    return links


def Mentor2_ISP(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio,NumNode, Limit, umin, alpha, debug):
    # 1. Tính Mentor 1 để lấy các nhóm backbone và truy nhập
    ListMentor, ListBackbone,center_node, special_traffic, traffic_matrix  = MENTOR.MenTor([Node_copy(n) for n in ListPosition], TrafficMatrix, MAX, C, w, RadiusRatio,NumNode, Limit, debug)
    # 2. Lấy ra các backbone node (node đầu tiên mỗi group)
    backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 3. Xây dựng các liên kết backbone theo Prim-Dijkstra
    prim_links = prim_dijkstra_backbone_links(ListPosition, backbone_nodes, ListMentor, center_node, alpha, MAX)
    plot_backbone(ListPosition,ListMentor, prim_links, MAX,None,None,None,None)
    backbone_links = prim_links.copy()
    direct_links = []
    backbone_links_compare = backbone_links.copy()
    traffic_matrix_compare = traffic_matrix.copy()
    # Tạo đồ thị backbone từ các liên kết backbone
    backbone_graph = nx.Graph()
    for n1, n2 in backbone_links:
        backbone_graph.add_edge(n1.get_name(), n2.get_name())
    
    
    # 4. Tính toán các liên kết trực tiếp bổ sung
    hop_list = []
    final_hop_list = []
    direct_links = []

    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            try:
                hops = nx.shortest_path_length(backbone_graph, source=u, target=v)
                hop_list.append((u, v, hops, traffic))
            except nx.NetworkXNoPath:
                print(f"Không tồn tại đường đi từ {u} đến {v} trên backbone.")
    
    # 1. Tách các cặp hops > 1 sang term_hop_list, còn lại là hops = 1
    term_hop_list = [item for item in hop_list if item[2] > 1]
    hop_list_1hop = [item for item in hop_list if item[2] == 1]
    # Sắp xếp theo số hops giảm dần
    term_hop_list.sort(key=lambda x: x[2], reverse=True)
    print(f"Term_hop_list trước khi xử lý: {term_hop_list}")
    hop_list.sort(key=lambda x: x[2], reverse=True)
    # In ra kết quả đã sắp xếp
    for u, v, hops, traffic in hop_list:
        print(f"Cặp backbone {u} - {v}: số hops = {hops}, traffic = {traffic_matrix.at[u,v]}")    
    print("------------------------------------------")

    while term_hop_list:
        u, v, hops, traffic = term_hop_list[0]
        n = math.ceil(traffic_matrix.at[u, v] / C)
        u_compare = traffic_matrix.at[u, v] / (n * C)
        u_compare = round(u_compare, 2)
        print(f"Cặp backbone {u} - {v}: traffic = {traffic_matrix.at[u, v]}")
        print(f"n = upperbound(T({u},{v})/C) = upperbound({traffic_matrix.at[u,v]}/{C}) = {n}")
        print(f"u= T({u},{v})/(n*C) = {traffic_matrix.at[u,v]}/({n}*{C}) = {u_compare:.2f}")
        if u_compare > umin:
            print("u > umin")
            print(f"Thêm liên kết trực tiếp {u} - {v}")
            direct_links.append((u, v))
            final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        else:
            print("u <= umin")
            print(f"Chuyển lưu lượng 1 hop qua mạng")
            path = nx.shortest_path(backbone_graph, source=u, target=v)
            min_dist = float('inf')
            home_node = None
            node_map = {n.get_name(): n for n in ListPosition}
            for i in range(1, len(path) - 1):
                home = path[i]
                # So sánh tổng khoảng cách Euclid
                dist_uhome = RadiusRatio * math.sqrt((node_map[u].get_position_x() - node_map[home].get_position_x())**2 +
                                        (node_map[u].get_position_y() - node_map[home].get_position_y())**2)
                dist_homev = RadiusRatio * math.sqrt((node_map[home].get_position_x() - node_map[v].get_position_x())**2 +
                                        (node_map[home].get_position_y() - node_map[v].get_position_y())**2)
                dist_sum = dist_uhome + dist_homev
                print(f"Cost({u},{home}) + Cost({home},{v}) = {dist_uhome:.2f} + {dist_homev:.2f} = {dist_sum:.2f}")
                if dist_sum < min_dist:
                    min_dist = dist_sum
                    home_node = home
            print(f"Nút home giữa {u} và {v} là {home_node}")
            # Cộng thêm traffic mới vào hai đoạn
            hops_uhome = nx.shortest_path_length(backbone_graph, source=u, target=home_node)
            hops_homev = nx.shortest_path_length(backbone_graph, source=home_node, target=v)
            traffic_sum_uhome = traffic_matrix.at[u, home_node] + traffic_matrix.at[u, v]
            traffic_sum_homev = traffic_matrix.at[home_node, v] + traffic_matrix.at[u, v]
            print(f"Lưu lượng sau cộng: T({u},{home_node}) = {traffic_matrix.at[u,home_node]} + {traffic_matrix.at[u,v]} = {traffic_sum_uhome}, T({home_node},{v}) = {traffic_matrix.at[home_node,v]} + {traffic_matrix.at[u,v]} = {traffic_sum_homev}")
            traffic_matrix.at[u, home_node] += traffic_matrix.at[u, v]
            traffic_matrix.at[home_node, v] += traffic_matrix.at[u, v]
            print(f"Số hops {u} - {home_node}: {hops_uhome}, {home_node} - {v}: {hops_homev}")
            if hops_uhome == 1:
                final_hop_list.append((u, home_node, traffic_matrix.at[u, home_node]))
            else:
                term_hop_list.append((u, home_node, hops_uhome, traffic_matrix.at[u, home_node]))
                
            if hops_homev == 1:
                final_hop_list.append((home_node, v, traffic_matrix.at[home_node, v]))
            else:
                term_hop_list.append((home_node, v, hops_homev, traffic_matrix.at[home_node, v]))
        # Sắp xếp lại cho vòng lặp tiếp theo
        term_hop_list = [item for item in term_hop_list if not ((item[0] == u and item[1] == v) or (item[0] == v and item[1] == u))]
        term_hop_list.sort(key=lambda x: x[2], reverse=True)
        print(f"Term_hop_list sau khi xử lý: {term_hop_list}")
        print("------------------------------------------")

    # 4. Sau khi xử lý xong, duyệt các cặp hops = 1 còn lại trong hop_list
    for u, v, hops, traffic in hop_list_1hop:
        print(f"Cặp backbone {u} - {v}, traffic {traffic_matrix.at[u,v]} có số hops = 1, chỉ thêm dung lượng.")
        print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        final_hop_list.append((u, v, traffic_matrix.at[u, v]))
        print("------------------------------------------")

    print("Xét lưu lượng các kết nối 1 hop:")
    for u, v, traffic in final_hop_list:
        n = math.ceil(traffic_matrix.at[u, v] / C)
        print(f"Cặp backbone {u} - {v}: T({u},{v})={traffic_matrix.at[u, v]}, n = upperbound(T({u},{v})/C) = upperbound({traffic_matrix.at[u,v]}/{C}) = {n}") 
    
    n_old_dict = {}
    for u, v, traffic in final_hop_list:
        n_old = math.ceil(traffic / C)
        n_old_dict[(u, v)] = n_old
        n_old_dict[(v, u)] = n_old  # 2 chiều
    calc_n_on_backbone_hops(backbone_links_compare, ListBackbone, traffic_matrix_compare, C)
    print_link_costs_with_n(backbone_links, direct_links, ListPosition, final_hop_list, C)
    plot_backbone(ListPosition, ListMentor, backbone_links, MAX, direct_links,True,final_hop_list,None)
    total_cost = 0
    total_cost_mentor = 0
    # for n1, n2 in backbone_links:
    #     dx = n1.get_position_x() - n2.get_position_x()
    #     dy = n1.get_position_y() - n2.get_position_y()
    #     dist = math.sqrt(dx*dx + dy*dy)
    #     total_cost += dist
    #     print(f"Tổng cost Prim_Dijkstra (Tổng khoảng cách Euclid các liên kết backbone): {total_cost}")
    direct_links_before = direct_links.copy()
    print("=== KẾT THÚC TÍNH TOÁN LIÊN KẾT TRỰC TIẾP ===")
    return  ListMentor,ListBackbone,special_traffic, traffic_matrix, n_old_dict,direct_links_before,backbone_links_compare


def plot_backbone(ListPosition, _list_mentor, backbone_links, MAX, direct_links,done,final_hop_list,compare):
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
        if compare is None:
            plt.title("Cây Prim-Dijkstra các nút backbone", fontsize=14)
        else:
            plt.title("Cây Prim-Dijkstra các nút backbone sau khi tăng dung lượng", fontsize=14)
    else:
        if compare is None:
            plt.title("Cây sau Mentor 1", fontsize=14)
        else:
            plt.title("Cây sau Mentor 1 sau khi tăng dung lượng", fontsize=14)

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

def Mentor_compare(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio,NumNode, Limit, umin, alpha,
                    debug,ListMentor, ListBackbone, special_traffic, traffic_matrix,n_old_dict,direct_links_before,backbone_links_compare):
    # 1. Tính Mentor 1 để lấy các nhóm backbone và truy nhập
    print("===================================================") 
    print("===================================================") 
    print("=== BẮT ĐẦU TĂNG LƯU LƯỢNG CÁC NÚT ===")
    print("===================================================") 
    print("===================================================")
    special_traffic += [
        (3, 20, 3),
        (13, 67, 4), 
        (15, 30, 3), 
        (40, 58, 5)
    ]
    print('special_traffic =', special_traffic)
    print("===================================================") 
    traffic_matrix = pd.DataFrame(0, index=ListBackbone, columns=ListBackbone)
    print("Backbone")
    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            # 1. Cộng traffic giữa backbone u và v
            traffic_matrix.at[u, v] += traffic
            traffic_matrix.at[v, u] += traffic  # Nếu 2 chiều
            print (u,'-',v,'traffic',traffic)
            # 2. Cộng thêm lưu lượng của các nút con thuộc nhóm u
          # Khởi tạo traffic_matrix
    # Khởi tạo traffic_matrix
    traffic_matrix = pd.DataFrame(0, index=ListBackbone, columns=ListBackbone)
    traffic_matrix.style.set_properties(**{'text-align': 'center'}).set_table_styles(
    [{'selector': 'th', 'props': [('text-align', 'center')]}]
)
    # Tạo từ điển để tra cứu nhanh lưu lượng giữa các cặp
    special_traffic_dict = {(u, v): t for u, v, t in special_traffic}
    special_traffic_dict.update({(v, u): t for u, v, t in special_traffic})  # 2 chiều

    # Duyệt từng cặp backbone (u, v)
    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            traffic_matrix.at[u, v] += traffic
            traffic_matrix.at[v, u] += traffic  # Nếu 2 chiều
            print("-----------------------------------------------") 
            print(f"{u}-{v} traffic {traffic}")
            # Tìm group chứa u và v
            group_u = next((g for g in ListMentor if g[0].get_name() == u), None)
            group_v = next((g for g in ListMentor if g[0].get_name() == v), None)
            if group_u is None or group_v is None:
                continue

            # Duyệt từng cặp node con (node_u, node_v)
            for node_u in group_u[1:]:  # bỏ backbone
                id_u = node_u.get_name()
                for node_v in group_v[1:]:
                    id_v = node_v.get_name()
                    if (id_u, id_v) in special_traffic_dict:
                        traffic = special_traffic_dict[(id_u, id_v)]
                        print(f"{id_u} <-> {id_v} traffic {traffic}")
                        traffic_matrix.at[u, v] += traffic
                        traffic_matrix.at[v, u] += traffic

                # ListTraffic.append(temp_traffic)
    print("======= Ma trận lưu lượng giữa các nút backbone =======")
    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            print(f"{u} <-> {v} traffic {traffic_matrix.at[u, v]}")
    print("=======================================================")
    print(traffic_matrix)
    print("\nTính moment và xác định nút backbone trung tâm:")
    moment_dict = {}
    center_node = None
    min_moment = float('inf')

    # Tạo map tên -> node để tiện truy xuất từ ListMentor
    name_to_node = {node.get_name(): node for group in ListMentor for node in group}

    for i in ListBackbone:
        moment = 0
        node_i = name_to_node[i]
        for j in ListBackbone:
            if i == j:
                continue
            node_j = name_to_node[j]
            dist = math.sqrt(
                (node_i.get_position_x() - node_j.get_position_x()) ** 2 +
                (node_i.get_position_y() - node_j.get_position_y()) ** 2
            )
            weight = node_j.get_traffic()
            moment += dist * weight
        moment_dict[i] = moment
        print(f"Moment({i}) = {moment:.4f}")
        if moment < min_moment:
            min_moment = moment
            center_node = node_i

    print(f"\n==> Nút backbone trung tâm là: {center_node.get_name()} với moment = {min_moment:.4f}")
    # 2. Lấy ra các backbone node (node đầu tiên mỗi group)
    backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 3. Xây dựng các liên kết backbone theo Prim-Dijkstra
    prim_links = prim_dijkstra_backbone_links(ListPosition, backbone_nodes, ListMentor, center_node, alpha, MAX)
    backbone_links = prim_links.copy()
    direct_links = []
    compare_backbone_links(backbone_links_compare, backbone_links, name1="Mentor2", name2="Mentor_compare")
    plot_backbone(ListPosition,ListMentor, prim_links, MAX,None,None,None,None)

    # Tạo đồ thị backbone từ các liên kết backbone
    backbone_graph = nx.Graph()
    for n1, n2 in backbone_links:
        backbone_graph.add_edge(n1.get_name(), n2.get_name())
    # 4. Tính toán các liên kết trực tiếp bổ sung
    hop_list = []
    final_hop_list = []
    direct_links = []

    for u, v, traffic in special_traffic:
        if u in ListBackbone and v in ListBackbone:
            try:
                hops = nx.shortest_path_length(backbone_graph, source=u, target=v)
                hop_list.append((u, v, hops, traffic))
            except nx.NetworkXNoPath:
                print(f"Không tồn tại đường đi từ {u} đến {v} trên backbone.")
    
    # 1. Tách các cặp hops > 1 sang term_hop_list, còn lại là hops = 1
    term_hop_list = [item for item in hop_list if item[2] > 1]
    hop_list_1hop = [item for item in hop_list if item[2] == 1]
    # Sắp xếp theo số hops giảm dần
    term_hop_list.sort(key=lambda x: x[2], reverse=True)
    print(f"Term_hop_list trước khi xử lý: {term_hop_list}")
    hop_list.sort(key=lambda x: x[2], reverse=True)
    # In ra kết quả đã sắp xếp
    for u, v, hops, traffic in hop_list:
        print(f"Cặp backbone {u} - {v}: số hops = {hops}, traffic = {traffic_matrix.at[u,v]}")    
    print("------------------------------------------")

    while term_hop_list:
        u, v, hops, traffic = term_hop_list[0]
        n = math.ceil(traffic_matrix.at[u, v] / C)
        u_compare = traffic_matrix.at[u, v] / (n * C)
        u_compare = round(u_compare, 2)
        print(f"Cặp backbone {u} - {v}: traffic = {traffic_matrix.at[u, v]}")
        print(f"n = upperbound(T({u},{v})/C) = upperbound({traffic_matrix.at[u,v]}/{C}) = {n}")
        print(f"u= T({u},{v})/(n*C) = {traffic_matrix.at[u,v]}/({n}*{C}) = {u_compare:.2f}")
        if u_compare > umin:
            print("u > umin")
            print(f"Thêm liên kết trực tiếp {u} - {v}")
            direct_links.append((u, v))
            final_hop_list.append((u, v, traffic_matrix.at[u, v]))
            print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        else:
            print("u <= umin")
            print(f"Chuyển lưu lượng 1 hop qua mạng")
            path = nx.shortest_path(backbone_graph, source=u, target=v)
            min_dist = float('inf')
            home_node = None
            node_map = {n.get_name(): n for n in ListPosition}
            for i in range(1, len(path) - 1):
                home = path[i]
                # So sánh tổng khoảng cách Euclid
                dist_uhome = RadiusRatio * math.sqrt((node_map[u].get_position_x() - node_map[home].get_position_x())**2 +
                                        (node_map[u].get_position_y() - node_map[home].get_position_y())**2)
                dist_homev = RadiusRatio * math.sqrt((node_map[home].get_position_x() - node_map[v].get_position_x())**2 +
                                        (node_map[home].get_position_y() - node_map[v].get_position_y())**2)
                dist_sum = dist_uhome + dist_homev
                print(f"Cost({u},{home}) + Cost({home},{v}) = {dist_uhome:.2f} + {dist_homev:.2f} = {dist_sum:.2f}")
                if dist_sum < min_dist:
                    min_dist = dist_sum
                    home_node = home
            print(f"Nút home giữa {u} và {v} là {home_node}")
            # Cộng thêm traffic mới vào hai đoạn
            hops_uhome = nx.shortest_path_length(backbone_graph, source=u, target=home_node)
            hops_homev = nx.shortest_path_length(backbone_graph, source=home_node, target=v)
            traffic_sum_uhome = traffic_matrix.at[u, home_node] + traffic_matrix.at[u, v]
            traffic_sum_homev = traffic_matrix.at[home_node, v] + traffic_matrix.at[u, v]
            print(f"Lưu lượng sau cộng: T({u},{home_node}) = {traffic_matrix.at[u,home_node]} + {traffic_matrix.at[u,v]} = {traffic_sum_uhome}, T({home_node},{v}) = {traffic_matrix.at[home_node,v]} + {traffic_matrix.at[u,v]} = {traffic_sum_homev}")
            traffic_matrix.at[u, home_node] += traffic_matrix.at[u, v]
            traffic_matrix.at[home_node, v] += traffic_matrix.at[u, v]
            print(f"Số hops {u} - {home_node}: {hops_uhome}, {home_node} - {v}: {hops_homev}")
            if hops_uhome == 1:
                final_hop_list.append((u, home_node, traffic_matrix.at[u, home_node]))
            else:
                term_hop_list.append((u, home_node, hops_uhome, traffic_matrix.at[u, home_node]))
                
            if hops_homev == 1:
                final_hop_list.append((home_node, v, traffic_matrix.at[home_node, v]))
            else:
                term_hop_list.append((home_node, v, hops_homev, traffic_matrix.at[home_node, v]))
        # Sắp xếp lại cho vòng lặp tiếp theo
        term_hop_list = [item for item in term_hop_list if not ((item[0] == u and item[1] == v) or (item[0] == v and item[1] == u))]
        term_hop_list.sort(key=lambda x: x[2], reverse=True)
        print(f"Term_hop_list sau khi xử lý: {term_hop_list}")
        print("------------------------------------------")

    # 4. Sau khi xử lý xong, duyệt các cặp hops = 1 còn lại trong hop_list
    for u, v, hops, traffic in hop_list_1hop:
        print(f"Cặp backbone {u} - {v}, traffic {traffic_matrix.at[u,v]} có số hops = 1, chỉ thêm dung lượng.")
        print(f"T({u},{v})={traffic_matrix.at[u, v]}")
        final_hop_list.append((u, v, traffic_matrix.at[u, v]))
        print("------------------------------------------")

    print("Xét lưu lượng các kết nối 1 hop:")
    for u, v, traffic in final_hop_list:
        n = math.ceil(traffic_matrix.at[u, v] / C)
        print(f"Cặp backbone {u} - {v}: T({u},{v})={traffic_matrix.at[u, v]}, n = upperbound(T({u},{v})/C) = upperbound({traffic_matrix.at[u,v]}/{C}) = {n}") 
    
    
    total_cost = 0
    total_cost_mentor = 0
    # for n1, n2 in backbone_links:
    #     dx = n1.get_position_x() - n2.get_position_x()
    #     dy = n1.get_position_y() - n2.get_position_y()
    #     dist = math.sqrt(dx*dx + dy*dy)
    #     total_cost += dist
    #     print(f"Tổng cost Prim_Dijkstra (Tổng khoảng cách Euclid các liên kết backbone): {total_cost}")
    print("=======================================")
    for u, v, traffic in final_hop_list:
        n_new = math.ceil(traffic / C)
        n_old = n_old_dict.get((u, v), None)
        if n_old is not None:
            if n_new != n_old:
                print(f"Liên kết {u}-{v}: n cũ = {n_old}, n mới = {n_new} => ĐÃ THAY ĐỔI")
            else:
                print(f"Liên kết {u}-{v}: n cũ = {n_old}, n mới = {n_new} => Không đổi")
        else:
            print(f"Liên kết {u}-{v}: n mới = {n_new} (không có ở lần chạy trước)")
    compare_direct_link_transitions(direct_links_before, direct_links)    
    plot_backbone(ListPosition, ListMentor, backbone_links, MAX, direct_links,True,final_hop_list,True)
    print("=== KẾT THÚC SO SÁNH ===")

    print("=== KẾT THÚC TÍNH TOÁN LIÊN KẾT TRỰC TIẾP ===")
    return backbone_names, ListMentor, prim_links, direct_links

def compare_direct_link_transitions(direct_links_before, direct_links_after):
    """
    So sánh sự thay đổi giữa hai trạng thái direct link:
    - Liên kết nào chuyển từ tăng dung lượng sang direct link (mới xuất hiện)
    - Liên kết nào chuyển từ direct link sang tăng dung lượng (không còn nữa)
    """
    set_before = set(tuple(sorted(link)) for link in direct_links_before)
    set_after = set(tuple(sorted(link)) for link in direct_links_after)

    # Liên kết mới xuất hiện (từ tăng dung lượng sang direct link)
    new_direct = set_after - set_before
    # Liên kết bị loại bỏ (từ direct link sang tăng dung lượng)
    removed_direct = set_before - set_after

    print("\n=== SO SÁNH CHUYỂN ĐỔI LIÊN KẾT TRỰC TIẾP ===")
    if new_direct:
        for u, v in new_direct:
            print(f"Liên kết {u}-{v} đã chuyển từ tăng dung lượng sang direct link.")
    else:
        print("Không có liên kết nào chuyển từ tăng dung lượng sang direct link.")

    if removed_direct:
        for u, v in removed_direct:
            print(f"Liên kết {u}-{v} đã chuyển từ direct link sang tăng dung lượng.")
    else:
        print("Không có liên kết nào chuyển từ direct link sang tăng dung lượng.")

def print_link_costs(backbone_links, direct_links, ListPosition):
    """
    Hiển thị giá ban đầu và giá thay đổi trên từng liên kết backbone ra terminal.
    Giá = round(0.3 * khoảng cách đề các)
    """
    # Tạo dict tra cứu vị trí node theo tên hoặc id
    node_map = {n.get_name(): n for n in ListPosition}

    print("\n=== BẢNG GIÁ LIÊN KẾT BACKBONE ===")
    print(f"{'Node1':>6} {'Node2':>6} {'Giá ban đầu':>12} {'Giá sau Mentor2':>18}")

    # Giá ban đầu: chỉ các backbone_links
    for n1, n2 in backbone_links:
        x1, y1 = node_map[n1.get_name()].get_position_x(), node_map[n1.get_name()].get_position_y()
        x2, y2 = node_map[n2.get_name()].get_position_x(), node_map[n2.get_name()].get_position_y()
        dist = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
        cost = round(0.3 * dist)
        print(f"{n1.get_name():>6} {n2.get_name():>6} {cost:>12} {'-':>18}")

    # Giá sau Mentor2: các direct_links (nếu có)
    for n1, n2 in direct_links:
        x1, y1 = node_map[n1].get_position_x(), node_map[n1].get_position_y()
        x2, y2 = node_map[n2].get_position_x(), node_map[n2].get_position_y()
        dist = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
        cost = round(0.3 * dist)
        print(f"{n1:>6} {n2:>6} {'-':>12} {cost:>18}")

    print("=== KẾT THÚC BẢNG GIÁ ===\n")

def print_link_costs_with_n(backbone_links, direct_links, ListPosition, final_hop_list, C):
    """
    Hiển thị giá ban đầu, số đường sử dụng (n), giá sau Mentor2 (tính theo n) trên từng liên kết backbone ra terminal.
    Giá = round(0.3 * khoảng cách đề các)
    """
    node_map = {n.get_name(): n for n in ListPosition}

    # Tạo dict tra cứu số đường sử dụng (n) và traffic trên từng liên kết
    n_dict = {}
    traffic_dict = {}
    for u, v, traffic in final_hop_list:
        n = math.ceil(traffic / C)
        n_dict[(u, v)] = n
        n_dict[(v, u)] = n  # 2 chiều
        traffic_dict[(u, v)] = traffic
        traffic_dict[(v, u)] = traffic

    print("=== BẢNG GIÁ LIÊN KẾT BACKBONE SAU MENTOR1 ===")
    print(f"{'Node1':>6} {'Node2':>6} {'Traffic':>12} {'N':>10} {'Cost':>12}")

    # Gom tất cả các link vào một set để duyệt chung
    all_links = set()
    for n1, n2 in backbone_links:
        all_links.add(tuple(sorted((n1.get_name(), n2.get_name()))))
    for n1, n2 in direct_links:
        all_links.add(tuple(sorted((n1, n2))))

    sum_cost = 0
    # Sắp xếp theo Node1, Node2 (giả sử tên node là số, nếu là chữ thì bỏ int())
    for u, v in sorted(all_links, key=lambda x: (int(x[0]), int(x[1]))):
        if u not in node_map or v not in node_map:
            continue
        x1, y1 = node_map[u].get_position_x(), node_map[u].get_position_y()
        x2, y2 = node_map[v].get_position_x(), node_map[v].get_position_y()
        dist = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
        n = n_dict.get((u, v), 1)
        traffic = traffic_dict.get((u, v), 0)
        total_cost = round(0.3 * dist) * n
        sum_cost += total_cost
        print(f"{u:>6} {v:>6} {traffic:>12} {n:>10} {total_cost:>12}")

    print(f"Total Cost: {sum_cost}")
    print("=== KẾT THÚC BẢNG GIÁ ===\n")

def calc_n_on_backbone_hops(backbone_links, ListBackbone, traffic_matrix, C):
    """
    Tính số đường (n) trên từng hop của cây backbone, kể cả các hop nằm giữa nhiều backbone.
    Các link không có traffic sẽ có n = 1.
    """
    import math
    import networkx as nx

    # Xây dựng đồ thị backbone
    G = nx.Graph()
    node_map = {}
    for n1, n2 in backbone_links:
        G.add_edge(n1.get_name(), n2.get_name())
        node_map[n1.get_name()] = n1
        node_map[n2.get_name()] = n2

    # Tạo dict lưu tổng traffic đi qua từng hop
    hop_traffic = {}
    # Duyệt từng cặp backbone có traffic (chỉ 1 chiều, i < j)
    for i in range(len(ListBackbone)):
        for j in range(i+1, len(ListBackbone)):
            u, v = ListBackbone[i], ListBackbone[j]
            # Lấy traffic một chiều duy nhất
            traffic = traffic_matrix.at[u, v] if hasattr(traffic_matrix, 'at') else traffic_matrix[u][v]
            if traffic > 0:
                try:
                    path = nx.shortest_path(G, source=u, target=v)
                    for k in range(len(path)-1):
                        a, b = path[k], path[k+1]
                        key = tuple(sorted((a, b)))
                        hop_traffic[key] = hop_traffic.get(key, 0) + traffic
                except nx.NetworkXNoPath:
                    continue

    # In kết quả cho các hop có traffic
    print("\n=== SỐ ĐƯỜNG TRÊN TỪNG HOP CỦA CÂY BACKBONE ===")
    print(f"{'Node1':>6} {'Node2':>6} {'Traffic':>10} {'N':>6} {'Cost':>10}")
    printed = set()
    sum_cost = 0

    # Gom tất cả các link (có traffic và không traffic) vào một set để duyệt chung
    all_links = set(tuple(sorted((a, b))) for (a, b) in hop_traffic.keys())
    for n1, n2 in backbone_links:
        all_links.add(tuple(sorted((n1.get_name(), n2.get_name()))))

    # Sắp xếp theo Node1, Node2 (giả sử tên node là số, nếu là chữ thì bỏ int())
    for a, b in sorted(all_links, key=lambda x: (x[0], x[1])):
        n1, n2 = node_map[a], node_map[b]
        dx = n1.get_position_x() - n2.get_position_x()
        dy = n1.get_position_y() - n2.get_position_y()
        dist = math.sqrt(dx*dx + dy*dy)
        traffic = hop_traffic.get((a, b), 0)
        n = math.ceil(traffic / C) if traffic > 0 else 1
        cost = round(0.3 * dist) * n
        sum_cost += cost
        print(f"{a:>6} {b:>6} {traffic:>10} {n:>6} {cost:>10}")

    print(f"Total Cost: {sum_cost}")
    return hop_traffic

def compare_backbone_links(links1, links2, name1="Mentor2", name2="Mentor_compare"):
    """
    So sánh hai danh sách backbone_links (dạng [(node1, node2), ...]) và in ra sự khác biệt.
    Nếu giống nhau hoàn toàn thì in "cây backbone không đổi".
    """
    set1 = set(tuple(sorted((n1.get_name(), n2.get_name()))) for n1, n2 in links1)
    set2 = set(tuple(sorted((n1.get_name(), n2.get_name()))) for n1, n2 in links2)

    only_in_1 = set1 - set2
    only_in_2 = set2 - set1

    if not only_in_1 and not only_in_2:
        print("CÂY BACKBONE KHÔNG ĐỔI")
        ("================================")
    else:
        print("\n=== SO SÁNH BACKBONE LINKS ===")
        if only_in_1:
            print(f"Chỉ có ở {name1}:")
            for u, v in sorted(only_in_1, key=lambda x: (int(x[0]), int(x[1]))):
                print(f"  {u} - {v}")
        if only_in_2:
            print(f"Chỉ có ở {name2}:")
            for u, v in sorted(only_in_2, key=lambda x: (int(x[0]), int(x[1]))):
                print(f"  {u} - {v}")
        print("=== KẾT THÚC SO SÁNH ===\n")

