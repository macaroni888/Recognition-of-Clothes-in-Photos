from Segmentation import seg
from PineCone.Search import search
import sys


def main(argc, argv):
    if argc != 2:
        print("Неправильное число аргументов. Ожидалось 2 аргумента")
    paths = seg.get_segm(argv[1], './masks')
    search(paths, argv[2])


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
