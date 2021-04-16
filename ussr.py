"""
Advanced Database system final project
"""
import numpy as np
import math
import datetime

header = datetime.datetime.now()
header_byte = bytes(str(header), 'utf-8')
Linear_hash_table = {}
rows = 10
columns = 10
Data_region = np.ndarray(shape=(rows, columns), dtype=bytearray)
current_empty = [0, 0]
max_block_size = 16


def insert_ussr(input_string, category):
    """
    The api function for inserting strings into the system

    :param input_string: user input string for inserting into the system
    :param category: either "inserted" or "updated", for returning message
    """
    my_bytes = bytes(input_string, 'utf-8')
    size = len(my_bytes)
    if size > max_block_size:
        res, code = handle_data_region_insert(my_bytes, True)
    else:
        res, code = handle_data_region_insert(my_bytes, False)

    if res:
        print(f'String {input_string} {category}.')
    else:
        if code == -1:
            print(f'String {input_string} cannot be {category} '
                  f'(excess the capacity of the system).')
        elif code == -2:
            print(f'String {input_string} cannot be {category} (System is full).')
        elif code == -3:
            print(f'String {input_string} already exists.')


def search_ussr(input_string):
    """
    The api function for searching a string in the system

    :param input_string: user input string for searching in the system
    """
    my_bytes = bytes(input_string, 'utf-8')
    res, _, _, _ = handle_data_region_search(my_bytes, True)

    if res:
        print(f'String {input_string} exists.')
    else:
        print(f'String {input_string} not exists.')


def update_ussr(old_string, new_string):
    """
    The api function for updating a string in the system

    :param old_string: the string that needs to update
    :param new_string: the new string is going to insert into the system
    """
    my_bytes = bytes(old_string, 'utf-8')
    handle_data_region_update(my_bytes, new_string)


def delete_ussr(input_string):
    """
    The api function for delete a string from the system

    :param input_string: the string that needs to delete
    """
    my_bytes = bytes(input_string, 'utf-8')
    res = handle_data_region_delete(my_bytes)
    if res:
        print(f'String {input_string} deleted.')
    else:
        print(f'String {input_string} cannot be deleted.')


def handle_data_region_insert(my_bytes, isExcess):
    """
    The main function for handling the process of insertion

    :param my_bytes: the string in byte array that going to insert into the system
    :param isExcess: boolean value for handling whether the strings needs multiple blocks
    :return: return ture and code = 0 if inserted, else return false and error code = -1 | -2 | -3
    """
    res, found_row, found_column, length = handle_data_region_search(my_bytes, False)
    if res:
        return True, -3
    if isExcess:
        tmp_len = len(my_bytes)
        if (rows - current_empty[0]) * columns - current_empty[1] < \
                math.ceil(tmp_len / max_block_size):
            return False, -2

        if check_is_full():
            return False, -1
        handle_hash_table([current_empty[0], current_empty[1]], math.ceil(tmp_len / max_block_size),
                          math.ceil(len(header_byte) / max_block_size))

        insert_cold_area(len(header_byte), header_byte)

        for part in range(0, tmp_len, max_block_size):
            current_bytes = my_bytes[:max_block_size]
            Data_region[current_empty[0], current_empty[1]] = current_bytes
            if not check_block_available():
                return False, -2
            my_bytes = my_bytes[max_block_size:]
    else:
        if check_is_full():
            return False, -1
        handle_hash_table([current_empty[0], current_empty[1]], 1,
                          math.ceil(len(header_byte) / max_block_size))

        insert_cold_area(len(header_byte), header_byte)

        Data_region[current_empty[0], current_empty[1]] = my_bytes
        if not check_block_available():
            return False, -2

    return True, 0


def handle_data_region_search(my_bytes, is_skip):
    """
    The main function for handling search functions

    :param my_bytes: the byte array for the string that needs to search in the system
    :param is_skip: boolean value for is needs to compare the hashes in code area
    :return: return true and the starting col, row and blocks of the data, else return false
    """
    chunks = [my_bytes[i:i + max_block_size] for i in range(0, len(my_bytes), max_block_size)]
    for pointer in Linear_hash_table.values():
        row, column, length, skip = pointer
        current_row = row
        current_column = column
        if is_skip:
            for sp in range(skip):
                current_row, current_column = get_next_hot_area(current_row, current_column)
                if current_row < 0:
                    return False, -1, -1, -1
        count = 0
        for index in range(length):
            if compare(Data_region[row][column], chunks[index], 'utf-8'):
                count += 1
                if column < columns - 1:
                    column += 1
                else:
                    row += 1
                    column = 0
            else:
                break
        if count == length:
            return True, current_row, current_column, length
    return False, -1, -1, -1


def handle_data_region_update(my_bytes, new_string):
    """
    The main function for handling string update in the system

    :param my_bytes: the byte array for the old string that needs to be update
    :param new_string: the new string that is going to insert into the system
    """
    if handle_data_region_delete(my_bytes):
        insert_ussr(new_string, 'Updated')


def handle_data_region_delete(my_bytes):
    """
    The main function for handling deletion in the system

    :param my_bytes: the string in byte array that is going to delete from the system
    :return: return true is delete is success else return false
    """
    global Linear_hash_table
    res, found_row, found_column, length = handle_data_region_search(my_bytes, True)
    if res:
        Linear_hash_table = {key: val for key, val in Linear_hash_table.items()
                             if val != [found_row, found_column, length]}

        row, column = found_row, found_column
        for _ in range(length):
            Data_region[row][column] = None
            if column < columns - 1:
                column += 1
            else:
                row += 1
                column = 0
        handle_hash_table_rebuild(found_row + found_column, length)
        handle_data_region_rebuild()
        return True
    return False


def handle_data_region_rebuild():
    """
    The main function that handler the rebuild of data region after string update or delete

    :return: return true is the data region is successfully rebuilt
    """
    global current_empty, Data_region
    tmp_region = Data_region.copy()
    Data_region = np.ndarray(shape=(rows, columns), dtype=bytearray)
    tmp_array = list(tmp_region)
    current_empty = [0, 0]
    for l_element in tmp_array:
        for element in l_element:
            if element is not None:
                Data_region[current_empty[0], current_empty[1]] = element
                if not check_block_available():
                    return False
    return True


def check_is_full():
    """
    The helper function to check if the data region is full

    :return: return true if the data region is full, else return false
    """
    if current_empty[0] >= rows and current_empty[1] >= columns:
        return True
    return False


def check_block_available():
    """
    The helper function to check if there is next block available in the data region

    :return: return true if that is next block available, else return false
    """
    current_empty[1] += 1
    if current_empty[1] >= columns:
        current_empty[0] += 1
        current_empty[1] = 0
        if current_empty[0] >= rows:
            return False
    return True


def get_next_hot_area(row, column):
    """
    The helper function to skip the cold areas and get to the first hot area block

    :return: return true if that is next block available, else return false
    """
    column += 1
    if column >= columns:
        row += 1
        column = 0
        if row >= rows:
            return -1, -1
    return row, column


def insert_cold_area(cold_len, cold_bytes):
    """

    :param cold_len: the byte length of the cold area
    :param cold_bytes: the bytes for the code area hashes
    :return: return true and code 0 if cold area hashes is inserted successfully, else
             return false and code -2 for not enough space
    """
    for part in range(0, cold_len, max_block_size):
        current_bytes = cold_bytes[:max_block_size]
        Data_region[current_empty[0], current_empty[1]] = current_bytes
        if not check_block_available():
            return False, -2
        cold_bytes = cold_bytes[max_block_size:]
    return True, 0


def handle_hash_table_rebuild(number, minus):
    """
    The main function for handling hash table rebuild after update or delete happened in data region

    :param number: the threshold of key for dictionary which needs to rebuild is key is larger
    :param minus: the count of blocks that is emptied because of the deletion
    """
    global Linear_hash_table
    tmp_table = Linear_hash_table.copy()
    for key in tmp_table:
        if key > number:
            current_update = Linear_hash_table.pop(key, None)
            Linear_hash_table.update(update_hash_table_index(current_update, minus))


def update_hash_table_index(array, minus):
    """
    The helper function for handling hash table rebuild

    :param array: contains the row, column, and block counts for the current data byte array
    :param minus: the count of blocks that is emptied because of the deletion
    :return: return the new dictionary item for updating the linear hash table
    """
    row, column, length = array
    for _ in range(minus):
        if column == 0:
            row -= 1
            column = columns - 1
        else:
            column -= 1
    return {row + column: [row, column, length]}


def handle_hash_table(value, length, skip):
    """
    The main function for updating hash table after insertion of strings in the data region

    :param value:  contains the row, column for the current data byte array
    :param length: the block counts for the current data byte array
    :param skip: blocks of hashes inside code area
    """
    tmp_dic = {current_empty[0] + current_empty[1]: value + [length, skip]}
    Linear_hash_table.update(tmp_dic)


def compare(a, b, encoding="utf8"):
    """
    The helper function for comparing byte arrays

    :param a: first byte to be compared
    :param b: second byte array to be compared
    :param encoding: type of encoding
    :return: return true if two byte array is equal, else return false
    """
    if isinstance(a, bytes):
        a = a.decode(encoding)
    if isinstance(b, bytes):
        b = b.decode(encoding)
    return a == b


if __name__ == '__main__':
    insert_ussr("Hello world!", "inserted")
    print(Data_region)
    print(Linear_hash_table)
    print()
    insert_ussr("ha ha ha ha ha ha", "inserted")
    print(Data_region)
    print(Linear_hash_table)
    print()
    insert_ussr("wow wow wow wow", "inserted")
    print(Data_region)
    print(Linear_hash_table)
    print()
    handle_data_region_delete(bytes("Hello world!", 'utf-8'))
    print(Data_region)
    print(Linear_hash_table)
    print()
    insert_ussr("Hello world!", "inserted")
    print(Data_region)
    print(Linear_hash_table)
    print()
    handle_data_region_update(bytes("Hello world!", 'utf-8'), 'Hello Mars!')
    print(Data_region)
    print(Linear_hash_table)
    print()
