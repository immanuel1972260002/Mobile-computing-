def aodv_discovery(source, destination, path):
    print(f'{source}: no valid route to {destination}; broadcast RREQ')
    for node in path[1:]:
        print(f'{node}: receive RREQ and record reverse route')
    print(f'{destination}: generate RREP')
    for node in reversed(path[:-1]):
        print(f'{node}: receive RREP and install forward route')
    print(f'{source}: route established via ' + ' -> '.join(path[1:]))

if __name__ == '__main__':
    aodv_discovery('S', 'D', ['S', 'A', 'D'])
