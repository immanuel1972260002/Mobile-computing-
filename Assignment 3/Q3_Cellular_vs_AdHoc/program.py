def select_architecture(infrastructure, deployment, multihop):
    if infrastructure == 'UNAVAILABLE' and deployment == 'IMMEDIATE':
        return 'AD_HOC'
    if multihop == 'REQUIRED':
        return 'AD_HOC'
    return 'CELLULAR'

if __name__ == '__main__':
    print('Selected architecture:', select_architecture('UNAVAILABLE', 'IMMEDIATE', 'REQUIRED'))
