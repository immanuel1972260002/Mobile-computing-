def update_route(table, destination, next_hop, received_hops, received_seq):
    new_hops = received_hops + 1
    old = table.get(destination)
    if old is None or received_seq > old['seq'] or (received_seq == old['seq'] and new_hops < old['hops']):
        table[destination] = {'next_hop': next_hop, 'hops': new_hops, 'seq': received_seq}
    return table

if __name__ == '__main__':
    routes = {}
    update_route(routes, 'D', 'B', 2, 8)
    print('A routing table:', routes)
