import os.path

from Segmentation import seg
from PineCone.Search import search
import sys
import shutil


def main(argc, argv):
    if argc != 3:
        print("Неправильное число аргументов. Ожидалось 2 аргумента")
        return
    if os.path.exists('./masks'):
        shutil.rmtree('./masks')
    paths = seg.get_segm(argv[1], './masks')
    if paths is None:
        return
    if len(paths) == 0:
        print("Не удалось найти одежду на изображении")
        return
    search(paths, argv[2])


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
