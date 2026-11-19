def simulate():
    packets = 10
    current_ap = 'AP1'
    delivered = lost = handoffs = 0
    for packet in range(1, packets + 1):
        if packet == 6 and current_ap != 'AP2':
            current_ap = 'AP2'
            handoffs += 1
        link_up = True
        if link_up:
            delivered += 1
            print(f'Packet {packet}: forwarded through {current_ap}')
        else:
            lost += 1
    print(f'Delivered={delivered}, Lost={lost}, Handoffs={handoffs}')

if __name__ == '__main__':
    simulate()
