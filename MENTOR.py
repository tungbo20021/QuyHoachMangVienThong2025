# Thư viện
import random
import math
import matplotlib.pyplot as plt
import Node
from NodesExcel import NodesExcel
from InitialTopo import Global_Init_Topo
import seaborn as sns
import pandas as pd

num_inf = math.inf
num_ninf = -math.inf

# Các cài đặt mặc định
def print_aligned_lists(list1, list2):
    # Đưa tất cả phần tử về dạng chuỗi
    str1 = [str(x) for x in list1]
    str2 = [str(x) for x in list2]

    # Tìm độ rộng lớn nhất của phần tử để căn lề
    max_width = max(max(len(s) for s in str1), max(len(s) for s in str2))

    # Tạo định dạng in ra
    format_str = f"{{:>{max_width}}}"

    # In list1
    print(' | '.join(format_str.format(x) for x in str1))
    # In list2
    print(' | '.join(format_str.format(x) for x in str2))

def MenTor(ListPosition,TrafficMatrix,MAX,C,w,RadiusRatio,NumNode,Limit,DeBug):
    ListMentor = []

    print("{:*<100}".format(''))
    print("Bước 2: Tìm Nút Backbone Và Các Nút Truy Nhập")
    print("{:*<100}".format(''))

    # Tạo ma trận lưu các nút backbone
    ListBackboneType1 = []

    for i in ListPosition:
        if i.get_traffic() / C > w:
            # i.print()
            ListBackboneType1.append(i)
            ListPosition.remove(i)

    if DeBug:
        print("2.1. List Backbone do lưu lượng chuẩn hóa lớn hơn ngưỡng")
        Node.printMentorList(ListBackboneType1)

    # Tìm MaxCost
    if DeBug:
        print("Tìm MaxCost và R*MaxCost")
    MaxCost = 0
    for i in range(len(ListPosition)):
        for j in range(i + 1, len(ListPosition)):
            dc = math.sqrt((ListPosition[i].get_position_x() - ListPosition[j].get_position_x()) ** 2 + (
                    ListPosition[i].get_position_y() - ListPosition[j].get_position_y()) ** 2)
            if dc > MaxCost:
                #print(ListPosition[i].get_name(), ListPosition[j].get_name(), dc)
                MaxCost = dc

    RM = RadiusRatio * MaxCost
    if DeBug:
        print('MaxCost = {:<8} & R*MaxCost = {:<8}'.format(round(MaxCost,3), round(RM,3)))

    # Dựng hàm cập nhật các nút đầu cuối cho các nút backbone
    DEBUG_UpdateTerminalNode = 0

    def updateTerminalNode(_ListPosition, _ListMentor, _centerNode):

        if DEBUG_UpdateTerminalNode:
            print("Enter Update Terminal Node Function! ")
            print("Node backbone", _centerNode.get_name())

        # Kiểm tra khoảng cách các node so với node backbone
        ListBackbone = []
        ListBackbone.append(_centerNode)

        def check_non_exist(index,listbackbone,listmentor):
            if DEBUG_UpdateTerminalNode:
                for i in listbackbone:
                    print(i.get_name(),end =' ')
                print()
                for i in listmentor:
                    for j in i:
                        print(j.get_name(), end=' ')
                print()
            for i in listbackbone:
                if i.get_name() == index:
                    if DEBUG_UpdateTerminalNode:
                        print("in list backbone. no check any more")
                    return False
            for i in listmentor:
                for j in i:
                    if j.get_name() == index:
                        if DEBUG_UpdateTerminalNode:
                            print("in list mentor. no check any more")
                        return False
            return True

        #Node.printList(_ListPosition)
        for i in _ListPosition:
            i.set_distance(_centerNode)
            if DEBUG_UpdateTerminalNode:
                print("Check Distance Node", i.get_name(), " : ", i.get_distance())
            if check_non_exist(i.get_name(),ListBackbone,_ListMentor):
                if i.get_distance() <= RM:
                    if DEBUG_UpdateTerminalNode:
                        print("Node", i.get_name(), "is terminal node of Node center", _centerNode.get_name())
                    ListBackbone.append(i)

        # Xử lý giới hạn số nút đầu cuối của nút backbone
        def sort_by_distance_to_backbone(m):
            return  m.get_distance()

        ListBackbone.sort(key=sort_by_distance_to_backbone)

        if Limit > 0:
            if DEBUG_UpdateTerminalNode:
                for i in ListBackbone:
                    print(i.get_name(),end =' ')
                print()
            if len(ListBackbone)-1 > Limit:
                ListBackbone = ListBackbone[0:Limit+1]
            if DEBUG_UpdateTerminalNode:
                for i in ListBackbone:
                    print(i.get_name(),end =' ')
                print()

        _ListMentor.append(ListBackbone)

        for i in ListBackbone:
            for j in _ListPosition:
                if i.get_name() == j.get_name():
                    _ListPosition.remove(j)

        if DEBUG_UpdateTerminalNode:
            print("Exit Update Terminal Node Function! ")

    for i in ListBackboneType1:
        updateTerminalNode(ListPosition, ListMentor, i)

    del ListBackboneType1
    if DeBug:
        print("-----------Nút Backbone Và Các Nút Truy Nhập -----------")
        Node.printList2D(ListMentor)
        print("-----------Các Nút Chưa Trong Cây Truy Nhập-----------")
        Node.printMentorList(ListPosition)


    if DeBug:
        print()
        print(
        "2.2. Tìm nút backbone trên giá trị thưởng và cập nhật lại cây truy nhập")
        print()
    center = Node.Node()
    iloop = 1
    while len(ListPosition) > 0:
        if DeBug:
            print("Vòng lặp tìm giá trị thưởng lần", iloop)
        iloop = iloop + 1
        # Tìm trung tâm trọng lực
        sumx = 0
        sumy = 0
        sumw = 0
        xtt = 0
        ytt = 0
        maxw = 1
        maxdc = 1
        maxaward = 0
        indexBB = 0

        for i in ListPosition:
            sumx = sumx + (i.get_position_x()) * i.get_traffic()
            sumy = sumy + (i.get_position_y()) * i.get_traffic()
            sumw = sumw + i.get_traffic()
            if i.get_traffic() > maxw:
                maxw = i.get_traffic()
        xtt = sumx / sumw
        ytt = sumy / sumw

        center.set_position(xtt, ytt)

        if DeBug:
            center.printCenterPress()

        for i in ListPosition:
            i.set_distance(center)
            if i.get_distance() > maxdc:
                maxdc = i.get_distance()
        if DeBug:
            print("MaxDistance = {:<6} & Max Weight: {:<3}".format(round(maxdc,2), maxw))
        for i in ListPosition:
            i.set_award((0.5 * (maxdc - i.get_distance() / maxdc)) + (0.5 * i.get_traffic() / maxw))
            if i.get_award() > maxaward:
                maxaward = i.get_award()

        for i in ListPosition:
            if i.get_award() >= maxaward:
                e = Node.Node()
                e.copyNode(i)
                if DeBug:
                    print("Nút Thưởng được chọn làm backbone: {:<3}".format(e.get_name()))
                ListPosition.remove(i)
                if DeBug:
                    print("--- Danh sách các nút còn lại ---")
                    Node.printMentorList(ListPosition)
                if DeBug:
                    print("---------------------")
                if DeBug:
                    print("Cập nhật cây truy nhập cho nút backbone mới")
                updateTerminalNode(ListPosition, ListMentor, e)
                if DeBug:
                    print("---------------------")
                    print("--- Danh sách các nút còn lại sau khi cập nhật cây truy nhập cho nút backbone mới ---")
                    Node.printMentorList(ListPosition)
                    print("---------------------")
                break


    if DeBug:
        print("-------Kết quả thuật toán Mentor-------")

        ListBackbone = []
    ListTraffic = []

    for group in ListMentor:
        if len(group) > 0:
            head = group[0].get_name()
            ListBackbone.append(head)  # Lưu tên hoặc ID của backbone
            rest = ' '.join(str(node.get_name()) for node in group[1:])
            # temp_traffic = 0
            # for node in group[1:]:
            #     temp_traffic += node.get_traffic()
            # ListTraffic.append(temp_traffic)
            print(f"{head} = {{{rest}}}")   

    special_traffic = []
    for i in range(NumNode):
        if i + 43 < NumNode:
            special_traffic.append((i, i + 43, 1))
        if i + 91 < NumNode:
            special_traffic.append((i, i + 91, 4))
        if i + 99 < NumNode:
            special_traffic.append((i, i + 99, 6))

    # Điều kiện thủ công
    special_traffic += [
        (8, 97, 46),
        (60, 88, 52),
        (20, 99, 30),
        (48, 29, 5)
    ]

    print('special_traffic =', special_traffic)

    # Tăng thêm lưu lượng cho các nút backbone tương ứng
    # for u, v, traffic in special_traffic:
    #     if u in ListBackbone and v in ListBackbone:
    #         index_u = ListBackbone.index(u)
    #         index_v = ListBackbone.index(v)
    #         print(u, v, traffic)
    #         ListTraffic[index_u] += traffic
    #         ListTraffic[index_v] += traffic

    print("===================================================")     
    # print_aligned_lists(ListBackbone, ListTraffic)

    # ======= TẠO MA TRẬN GIAO CẮT =======
    # Tạo DataFrame lưu lượng giữa các nút backbone
    # Khởi tạo traffic_matrix
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


    NodesExcel.backbones_to_excel("nodes_inf.xlsx", ListMentor)
    Node.matplot_mentor(ListMentor,MAX)

    # Node.plt.show()
    return ListMentor, ListBackbone, center_node, special_traffic, traffic_matrix



