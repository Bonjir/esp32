
char_dict = {
    ' ' : 0, '!' : 6, '"' : 12, '#' : 18, '$' : 24, '%' : 30, '&' : 36, '\'': 42, 
    '(' : 48, ')' : 54, '*' : 60, '+' : 66, ',' : 72, '-' : 78, '.' : 84, '/' : 90, '0' : 96, 
    '1' : 102, '2' : 108, '3' : 114, '4' : 120, '5' : 126, '6' : 132, '7' : 138, '8' : 144, '9' : 150, 
    ':' : 156, ';' : 162, '<' : 168, '=' : 174, '>' : 180, '?' : 186, '@' : 192, 'A' : 198, 'B' : 204, 
    'C' : 210, 'D' : 216, 'E' : 222, 'F' : 228, 'G' : 234, 'H' : 240, 'I' : 246, 'J' : 252, 'K' : 258, 
    'L' : 264, 'M' : 270, 'N' : 276, 'O' : 282, 'P' : 288, 'Q' : 294, 'R' : 300, 'S' : 306, 'T' : 312, 
    'U' : 318, 'V' : 324, 'W' : 330, 'X' : 336, 'Y' : 342, 'Z' : 348, '[' : 354, '\\': 360, ']' : 366, 
    '^' : 372, '_' : 378, '`' : 384, 'a' : 390, 'b' : 396, 'c' : 402, 'd' : 408, 'e' : 414, 'f' : 420, 
    'g' : 426, 'h' : 432, 'i' : 438, 'j' : 444, 'k' : 450, 'l' : 456, 'm' : 462, 'n' : 468, 'o' : 474, 
    'p' : 480, 'q' : 486, 'r' : 492, 's' : 498, 't' : 504, 'u' : 510, 'v' : 516, 'w' : 522, 'x' : 528, 
    'y' : 534, 'z' : 540, 'horiz line' : 546, 'degreec-first-half' : 552, 'degreec-second-half' : 558
}

if __name__ == '__main__':
    while True:
        char = "null"
        while char not in char_dict:
            char = input("input a char: ")
        
        filename = "codetab.bin"
        with open(filename, "rb") as fb:
            fb.seek(char_dict[char], 0)
            char_bytes = []
            for col in range(0, 6):
                char_bytes.append(int.from_bytes(fb.read(1), "little"))
            print("'{}': {}".format(char, char_bytes))
        
    # read all codetab
    # with open(filename, "rb") as fb:
    #     for letter in range(0,85):
    #         char_bytes = []
    #         for col in range(0, 6):
    #             char_bytes.append(int.from_bytes(fb.read(1), "little"))
    #         print("{}".format(char_bytes))