import Node
import InitialTopo
import MENTOR
import argparse
import matplotlib.pyplot as plt
import matplotlib
import Mentor_2
matplotlib.use('TkAgg')

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
    ListMentor, ListBackbone,special_traffic, traffic_matrix = Mentor_2.Mentor2_ISP(
        ListPosition, TrafficMatrix, args.max, args.C, args.w, args.radius,args.num_node, args.limit_mentor,
        args.umin , args.alpha, debug=args.debug
    )
    
    Mentor_2.Mentor_compare(ListPosition, TrafficMatrix, args.max, args.C, args.w, args.radius,args.num_node, args.limit_mentor,
        args.umin , args.alpha, args.debug, ListMentor, ListBackbone, special_traffic, traffic_matrix)

# Giả sử bạn đã có ListPosition và MAX từ bước tạo topology
if __name__ == '__main__':
    main()
