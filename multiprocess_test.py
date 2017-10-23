from multiprocessing import Process
def mp(name='default'):
    print('hell', name)
def main():
    p = Process(target=mp, args=('bob'))
    p.start()
    p.join()
if __name__ == "__main__":
    main()