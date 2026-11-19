def mobile_ip():
    home_address = '10.0.0.8'
    care_of_address = '192.0.2.9'
    registration_accepted = True
    binding = {}
    if not registration_accepted:
        print('REGISTRATION_FAILURE')
        return
    binding[home_address] = care_of_address
    print(f'HA binding: {home_address} -> {binding[home_address]}')
    print('CN sends packet to home address')
    print(f'HA encapsulates and tunnels packet to {care_of_address}')
    print('Tunnel endpoint decapsulates packet')
    print('Packet delivered to Mobile Node: DELIVERY_SUCCESS')

if __name__ == '__main__':
    mobile_ip()
