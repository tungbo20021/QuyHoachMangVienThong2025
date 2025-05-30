# Thư viện
import random
import math
import matplotlib.pyplot as plt
import Node
from NodesExcel import NodesExcel


def sortListPosition(m):
    return m.get_position_x()

def Global_Init_Topo(MAX,NumNode,DeBug):

    print("{:*<100}".format(''))
    print("Bước 1: Xây dựng node ngẫu nhiên và tính toán lưu lượng từng nút")
    print("{:*<100}".format(''))
    ListPosition = []

    # Tạo các nút ở vị trí random và đưa vào danh sách, sắp xếp các nút theo thứ tự tọa độ x tăng dần
    for i in range(NumNode):
        n = Node.Node()
        n.create_position(MAX)
        n.create_name(i + 1)
        ListPosition.append(n)
      # ListPosition.sort(key=sortListPosition)
  
    # Tạo ma trận lưu trữ thông tin về lưu lượng giữa các nút.
    TrafficMatrix = [[0] * NumNode for i in range(NumNode)]

    # for i in TrafficMatrix:
    #     for j in i:
    #         print(j,end=' ')
    #     print()

    # Đưa thông tin lưu lượng vào ma trận
    def set_traffic(m, n, value):
        TrafficMatrix[m - 1][n - 1] = value
        TrafficMatrix[n - 1][m - 1] = value

    def set_traffic0(m, n, value):
        TrafficMatrix[m][n] = value
        TrafficMatrix[n][m] = value

    for i in range(NumNode):

        if i + 43 < NumNode:
            set_traffic0(i, i + 43, 1)
        if i + 91 < NumNode:
            set_traffic0(i, i + 91, 4)
        if i + 99 < NumNode:
            set_traffic0(i, i + 99, 6)

    set_traffic(8, 97, 46)
    set_traffic(60, 88, 52)
    set_traffic(20, 99, 30)
    set_traffic(48, 29, 5)
 
    # tính lưu lượng của mỗi nút và cập nhật vào nút

    for i in range(len(ListPosition)):
        ListPosition[i].set_traffic(sum(TrafficMatrix[ListPosition[i].get_name() - 1]))
        # ListPosition[i].print()

    if DeBug:

        print("---------Topology mạng-------------")
        Node.printInitialList(ListPosition)
        NodesExcel.nodes_to_excel(ListPosition,'nodes_inf.xlsx')
        print("----------Kết thúc tạo topology-------------")

    Node.matplotList(ListPosition, MAX)
    Node.plt.show()
    return ListPosition, TrafficMatrix
