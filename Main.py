import Node
import InitialTopo
import MENTOR
import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

import Mentor_2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=1000, help='Thong so mat phang MAX x MAX')
    parser.add_argument('--num_node', type=int, default=100, help='So nut trong mang')
    parser.add_argument('--radius', type=float, default=0.3, help='Ty le de tinh ban kinh trong Mentor')
    parser.add_argument('--C', type=int, default=25, help='Dung luong 1 lien ket')
    parser.add_argument('--w', type=int, default=2, help='Trong so luu luong chuan hoa de xet nut backbone của MENTOR')
    parser.add_argument('--limit_mentor', type=int, default=0, help='Gioi han cua thuat toan mentor')
    parser.add_argument('--debug', type=bool, default=True, help='Che do Debug')
    parser.add_argument('--umin', type=int, default=0.8,help='')
    parser.add_argument('--alpha', type=int, default=0.2,help='')
    return parser.parse_args()

def main():
    args = parse_args()
    # Tạo topology ngẫu nhiên
    ListPosition, TrafficMatrix = InitialTopo.Global_Init_Topo(args.max, args.num_node, args.debug)
    
    # Lấy đủ 8 giá trị trả về
    backbone, link_path_count, link_cost, link_cost_changed, link_usage, ListMentor, prim_links, _ = Mentor_2.Mentor2_ISP(
        ListPosition, TrafficMatrix, args.max, args.C, args.w, args.radius,args.num_node, args.limit_mentor,
        args.umin , args.alpha, debug=args.debug
    )
    
    # Xuất kết quả ra file (nếu muốn)
    # Mentor_2.write_result('mentor2_result.txt', backbone, link_path_count, link_cost, link_cost_changed, link_usage)
    # print("Đã xuất kết quả Mentor 2 ra mentor2_result.txt")

    # # Đọc liên kết bổ sung từ file
    # direct_links = read_direct_links('mentor2_result.txt', ListPosition)
    # # Lọc các direct_links không có trong prim_links
    # prim_set = set((min(n1.get_name(), n2.get_name()), max(n1.get_name(), n2.get_name())) for n1, n2 in prim_links)
    # filtered_direct_links = []
    # for n1, n2 in direct_links:
    #     key = (min(n1.get_name(), n2.get_name()), max(n1.get_name(), n2.get_name()))
    #     if key not in prim_set:
    #         filtered_direct_links.append((n1, n2))

    # print("Số liên kết trực tiếp bổ sung:", len(filtered_direct_links))
    # print("Danh sách direct_links:", [(n1.get_name(), n2.get_name()) for n1, n2 in filtered_direct_links])

    # # Vẽ cả prim_links (xám) và direct_links (đỏ)
    # Mentor_2.plot_backbone_full(ListPosition, ListMentor, prim_links, filtered_direct_links, args.max)
    # plt.show()
    
# def read_result_file(filename):
#     links = []
#     with open(filename, 'r', encoding='utf-8') as f:
#         next(f)  # Bỏ qua dòng tiêu đề
#         for line in f:
#             parts = line.strip().split('\t')
#             if len(parts) >= 1 and '-' in parts[0]:
#                 n1, n2 = map(int, parts[0].split('-'))
#                 links.append((n1, n2))
#     return links

# def read_direct_links(filename, ListPosition):
#     node_map = {n.get_name(): n for n in ListPosition}
#     links = []
#     with open(filename, 'r', encoding='utf-8') as f:
#         next(f)  # Bỏ qua dòng tiêu đề
#         for line in f:
#             parts = line.strip().split('\t')
#             if len(parts) >= 1 and '-' in parts[0]:
#                 n1, n2 = map(int, parts[0].split('-'))
#                 if n1 in node_map and n2 in node_map:
#                     links.append((node_map[n1], node_map[n2]))
#     return links

# def plot_links(ListPosition, links, MAX, ListMentor):
#     colors = ['red', 'blue', 'green', 'orange', 'purple', 'magenta', 'lime', 'brown', 'cyan', 'pink']
#     node_map = {n.get_name(): n for n in ListPosition}

#     # Xác định các nút backbone (node đầu tiên của mỗi group)
#     backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]

#     # Vẽ các node theo nhóm với màu khác nhau
#     for idx, group in enumerate(ListMentor):
#         color = colors[idx % len(colors)]
#         for n in group:
#             x, y = n.get_position_x(), n.get_position_y()
#             if n in backbone_nodes:
#                 # Vẽ backbone node nổi bật: viền đen, lớn hơn
#                 plt.plot(x, y, 's', color=color, markersize=20, markeredgewidth=3, markeredgecolor='grey', zorder=5)
#                 plt.text(x, y, str(n.get_name()), fontsize=14, color='black', ha='center', va='center', fontweight='bold', zorder=6)
#             else:
#                 plt.plot(x, y, 's', color=color, markersize=14, zorder=4)
#                 plt.text(x, y, str(n.get_name()), fontsize=10, color='black', ha='center', va='center', fontweight='bold', zorder=5)

#     # Vẽ các liên kết backbone
#     for n1, n2 in links:
#         x1, y1 = node_map[n1].get_position_x(), node_map[n1].get_position_y()
#         x2, y2 = node_map[n2].get_position_x(), node_map[n2].get_position_y()
#         plt.plot([x1, x2], [y1, y2], 'k-', linewidth=3, zorder=3)

#     plt_margin = MAX * 0.05
#     plt.axis([-plt_margin, MAX + plt_margin, -plt_margin, MAX + plt_margin])
#     plt.title("Các nút backbone sau Mentor 2 ISP", fontsize=14)
#     plt.xlabel("X")
#     plt.ylabel("Y")
#     plt.grid(True)
#     plt.show()

# Giả sử bạn đã có ListPosition và MAX từ bước tạo topology
if __name__ == '__main__':
    main()
