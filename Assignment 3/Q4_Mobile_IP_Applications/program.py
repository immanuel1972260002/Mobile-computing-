def ambulance_communication():
    home = '10.1.0.20'
    coa = '198.51.100.20'
    registered = True
    packet = 'Patient status + GPS location'
    if not registered:
        print('Packet buffered: registration failed')
        return
    print(f'Register {home} -> {coa} with Home Agent')
    print(f'HA tunnels emergency packet to {coa}')
    print(f'Dispatch centre receives: {packet}')
    print('Result: DELIVERY_SUCCESS')

if __name__ == '__main__':
    ambulance_communication()
