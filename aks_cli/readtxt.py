def read():
    with open('log.txt', 'r', encoding='utf-8') as f:
        c = f.read()
    print(c)
    return c


if __name__ == '__main__':
    read()