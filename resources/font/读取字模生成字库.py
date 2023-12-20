import numpy as np
import re

codetab_size = 94
fontw = 6

def format_read2(filename): # 6x8
    file = open(filename)
    lines = file.readlines()
    n_lines = len(lines)
    data = np.zeros((codetab_size, fontw))
    # chr_dict = {}
    index_dict = {}
    index = 0
    for line in lines:
        line = line.strip()
        correspond_chr = re.findall("// (.*)", line)
        index_dict[index] = correspond_chr
        line = re.findall("(.*?)//", line)[0][0:-2]
        one = line.split(', ')
        print("{}: {}".format(index_dict[index], one))
        for i in range(0, len(one)):
            hex = one[i]
            data[index, i] = int(hex, 16)
        index += 1
    file.close()
    return data, index_dict

def format_read(filename): #16x16
    file = open(filename)
    lines = file.readlines()
    n_lines = len(lines)
    data = np.zeros((26, 16))
    index = 0
    for line in lines:
        line = line.strip()
        if not len(line) or line[0] != 'D':
            continue
        line = line[3:-7]
        one = line.split('H ')
        for i in range(0, len(one) - 1):
            data[index, i] = int(one[i], 16)
            # print(int(one[i], 16))
        index += 1
    file.close()
    return data

if __name__ == '__main__':
    filename = "字模.txt"
    data, index_dict = format_read2(filename)
    print(data)
    with open("codetab.bin", "wb") as fb:
        for letter in range(0, codetab_size):
            for col in range(0, fontw):
                int_dat = int(data[letter, col])
                # print("{}: {}".format(int_dat, int.from_bytes(int_dat.to_bytes(1, "little"), "little")))
                fb.write(int_dat.to_bytes(1, "little"))
    for i in index_dict:
        if index_dict[i][0] == 'space':
            index_dict[i][0] = ' '
        print("'{}' : {},".format(index_dict[i][0], i * fontw), end = ' ')
    # for letter in range(0, 26):
    #     for col in range(0, 8):
    #         print
