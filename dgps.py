"""
Domain-Guided Prefix Suppression
log2(dmax − dmin + 1) = 6
"""
import random
import numpy as np
import math

Hash_table = {}
ascii_start = 65


def generate_table(table_count, table_size, min_value, max_value):
    for count in range(table_count):
        My_list = random.sample(range(min_value, max_value), table_size)
        Hash_table.update({chr(ascii_start + count): My_list})


def sim_suppression(table_one_index, table_two_index):
    list_one = Hash_table[chr(ascii_start + table_one_index)]
    list_two = Hash_table[chr(ascii_start + table_two_index)]
    numpy_array1 = np.asarray(list_one, dtype=int)
    numpy_array2 = np.asarray(list_two, dtype=int)
    min_max_one, value = get_norm([np.amin(numpy_array1), np.max(numpy_array1)])
    numpy_array1 = numpy_array1 + value
    min_max_two, value = get_norm([np.amin(numpy_array2), np.max(numpy_array2)])
    numpy_array2 = numpy_array2 + value

    bit_one = math.ceil(math.log2(min_max_one[1]))
    bit_two = math.ceil(math.log2(min_max_two[1]))
    in_shift, out_shift = 0, 0
    if bit_one > bit_two:
        in_shift = math.ceil(math.log2(min_max_two[1]) + 1)
    elif bit_two > bit_one:
        out_shift = math.ceil(math.log2(min_max_one[1]) + 1)
    join = sim_packing(numpy_array1, numpy_array2, in_shift, out_shift)

# void pack2_i32_i16_to_i32(i32* res, int n,
# i32* col1, i32 b1, int ishl1, int oshr1, i32 m1,
# i16* col2, i16 b2, int ishl2, int oshr2, i32 m2) {
# for (int i=0; i<n; i++) {
# // Select portion of input and cast to result's type
# i32 c1 = ((col1[i] - b1) >> ishl1) & m1;
# i32 c2 = ((col2[i] - b2) >> ishl2) & m2;
# // Move to output positions
# res[i] = (c1 << oshr1) | (c2 << oshr2);
# } }
def sim_packing(numpy_array1, numpy_array2, in_shift, out_shift):
    join = []
    mask = 0xFFFFFFFFF
    for element1, element2 in zip(numpy_array1, numpy_array2):
        bits1 = (element1 >> in_shift) & mask
        bits2 = (element2 >> in_shift) & mask
        join.append((bits1 << out_shift) | (bits2 << out_shift))
    return join


# void unpack2_i32_i16_to_i16(i16* res, int n, int* idx, i16 b,
# i32* col1, int ishr1, int oshl1, i16 m1, int s1,
# i16* col2, int ishr2, int oshl2, i16 m2, int s2) {
# for (int i=0; i<n; i++) {
# // DSM (columnar) position -> NSM (row) position
# int idx1 = idx[i] * s1;
# int idx2 = idx[i] * s2;
# // Extract relevant bits from NSM record
# i16 c1 = (col1[idx1] >> ishr1) & m1;
# i16 c2 = (col2[idx2] >> ishr2) & m2;
# // Stitch back together
# res[i] = (c1 << oshl1) | (c2 << oshl2) + b;
# } }
def sim_unpacking():
    pass


def get_norm(array):
    if array[0] > 0:
        return [0, array[1] - array[0]], -array[0]
    else:
        return [0, array[1] + abs(array[0])], abs(array[0])


if __name__ == '__main__':
    generate_table(3, 10, -1000, 1000)
    sim_suppression(0, 2)