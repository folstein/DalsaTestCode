import os
import fnmatch
from PIL import Image, ImageChops
import argparse
import numpy as np
from pathlib import Path


origBmps = R"C:\Dump\Projects\00 Genie 12M compression pics 22-05-18\test - bmps"

# olds = R"C:\Dump\Projects\00 Dalsa 45M compression pics 22-05-23\test2 - old\bmps"
# news = R"C:\Dump\Projects\00 Dalsa 45M compression pics 22-05-23\test2 - run\bmps"
olds = R"C:\Dump\NoBackup\Projects\00 Genie 12M compression pics 22-05-18\test2 - run\bmps-old"
news = R"C:\Dump\NoBackup\Projects\00 Genie 12M compression pics 22-05-18\test2 - run\bmps-new"

# old45 = R"C:\Dump\Projects\00 Dalsa 45M compression pics 22-05-23\test - old\bmps"
# new45 = R"C:\Dump\Projects\00 Dalsa 45M compression pics 22-05-23\test - runs\bmps"
# old12 = R"C:\Dump\Projects\00 Genie 12M compression pics 22-05-18\test - olds\bmps"
# new12 = R"C:\Dump\Projects\00 Genie 12M compression pics 22-05-18\test - runs\bmps"

paths = R"C:\Dump\Projects\00 Genie 12M compression pics 22-05-18\test2 - run\bmps"

def main1():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()

    ap.add_argument("first", help="image 1")
    ap.add_argument("second", help="image 2")
    ap.add_argument("output", help="output")

    args = ap.parse_args()

    compare(args.first, args.second, args.output)


def main2(path1: str, path2: str):
    for filename in fnmatch.filter(os.listdir(path1), '*.bmp'):
        f1 = os.path.join(path1, filename)
        f2 = os.path.join(path2, filename)
        op = str(Path(f1).with_stem(Path(f1).stem + '_diff').with_suffix('.txt'))

        if os.path.isfile(f1) and os.path.isfile(f2):
            compare(f1, f2, op, True, 1)


def main(path: str):
    for filename in fnmatch.filter(os.listdir(path), '*.bmp'):
        if "_oldrc" in filename or "_diff" in filename:
            continue
        f1 = os.path.join(path, filename)
        f2 = os.path.join(path, filename.replace("_sl", "_oldrc_sl"))
        op = str(Path(f1).with_stem(Path(f1).stem + '_diff').with_suffix('.txt'))

        if os.path.isfile(f1) and os.path.isfile(f2):
            compare(f1, f2, op, True, 0)

        if "_sl01" in filename:
            ob = os.path.join(origBmps, filename.replace("_sl01", ""))
            op = str(Path(f1).with_stem(Path(ob).stem + '_diff').with_suffix('.txt'))
            compare(f1, ob, op, True, 1)

            op = str(Path(f2).with_stem(Path(ob).stem + '_oldrc_diff').with_suffix('.txt'))
            compare(f2, ob, op, True, 1)


def compare(first: str, second: str, output: str, diffBmp: bool, firstCol: int):

    imageA = Image.open(first)
    imageB = Image.open(second)
    # nCol, nRow = imageA.size

    # open the images as arrays and drop the last two columns
    pixA = np.asarray(imageA, dtype=np.int16)[:, firstCol:-2]
    pixB = np.asarray(imageB, dtype=np.int16)[:, firstCol:-2]

    pixDiff = pixA - pixB

    sumDiff = np.absolute(pixDiff).sum(axis=1)

    if sumDiff.sum() != 0:
        print(f"{Path(first).stem} {sumDiff.sum()}")
        with open(output, 'w') as outfile:
            it = np.nditer(pixDiff, flags=['multi_index'])
            for x in it:
                if x != 0:
                    outfile.write(f"{x} {it.multi_index}\n")

        if diffBmp:
            diff = ImageChops.subtract(imageA, imageB, 0.05, 100)
            if os.path.isfile(Path(output).with_suffix('.bmp')):
                os.remove(Path(output).with_suffix('.bmp'))
            diff.save(Path(output).with_suffix('.bmp'))

    #     it = np.nditer(pixDiff, flags=['multi_index'])
    #     for x in it:
    #         #idx = it.multi_index
    #         if x == 0: # or it.multi_index[1] in ignoreCols:
    #             continue
    #         outfile.write("%d %s\n" % (x, it.multi_index))


    # if diff.getbbox():
    #     diff.show()

def test():
    bmp = os.path.join(origBmps, "Frm16_on_s64k_p160.bmp")

    image = Image.open(bmp)
    nCol, nRow = image.size

    # open the images as arrays and drop the last two columns
    pixs = np.asarray(image, dtype=np.int16)

    op = str(Path(bmp).with_suffix('.cpp'))

    with open(op, 'w') as outfile:
        outfile.write(f"unsigned char src[5][{nCol}] = {{\n")
        for c in range(109, 114):
            row = pixs[c]
            
            output = "{\n"
            count = 32

            for v in row:
                output += f"{v:3},"
                count = count - 1
                if count <= 0:
                    count = 32
                    output += "\n"
                    outfile.write(output)
                    output = ""
            
            outfile.write("},\n")
        outfile.write("};\n")


if __name__ == "__main__":
    #main(paths)
    main2(news, olds)
    #main(new12, old12)

    #test()
