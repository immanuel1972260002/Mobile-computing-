def emergency_network():
    generated = 5
    delivered = 0
    control = 0
    route = ['Ambulance', 'Relay-1', 'Relay-2', 'Field-Hospital']
    print('Fixed infrastructure: UNAVAILABLE')
    print('AODV: broadcast RREQ for first data packet')
    control += 1
    print('RREP received; route:', ' -> '.join(route))
    control += 1
    for packet in range(1, generated + 1):
        delivered += 1
        print(f'Packet {packet}: delivered to Field-Hospital')
    print('Generated:', generated)
    print('Delivered:', delivered)
    print('Packet delivery ratio:', f'{delivered/generated*100:.1f}%')
    print('Control messages (simplified count):', control)

if __name__ == '__main__':
    emergency_network()
