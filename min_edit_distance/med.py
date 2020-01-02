import argparse
from copy import deepcopy


def ins_cost():
    return 1

def del_cost():
    return 1

def sub_cost(si, ti):
    return 0 if ti == si else 2

def min_of_3(a, b, c):
    result_val = min(a, min(b,c))
    if b == result_val:
        return result_val, 1  # sub

    if a == result_val:
        return result_val, 0  # delete

    return result_val, 2  # insert

def minimum_edit_distance(target, source):
    n = len(target)
    m = len(source)
    dis_mat = [[0 for x in range(n+2)] for y in range(m+2)]
    track_map = [[0 for x in range(n+2)] for y in range(m+2)]

    # initialize
    target = '#' + target
    source = '#' + source

    dis_mat[0][0] = '.'
    dis_mat[0][1:] = target

    for i in range(1, m + 2):
        dis_mat[i][0] = source[i-1]

    dis_mat[1][1] = 0
    for i in range(2, n+2):
        dis_mat[1][i] = dis_mat[1][i-1] + ins_cost()
        track_map[1][i] = 2 # insert tracking

    for i in range(2, m+2):
        dis_mat[i][1] = dis_mat[i-1][1] + del_cost()
        track_map[i][1] = 0 # delete tracking

    for i in range(2, m+2):
        for j in range(2, n+2):
            dis_mat[i][j], track_map[i][j] = min_of_3(dis_mat[i-1][j] + del_cost(),
                    dis_mat[i-1][j-1] + sub_cost(source[i-1], target[j-1]),
                    dis_mat[i][j-1] + ins_cost())

    # display mat
    print(70 * "=")
    print("Distance matrix:")
    print('\n'.join([''.join(['{:4}'.format(str(item)) for item in row])
      for row in dis_mat]))

    print(70 * "=")
    print('Minimum edit distance: ', dis_mat[m+1][n+1])
    # display step
    i, j = m + 1, n + 1
    source_str = list()
    target_str = list()
    todo_str = list()
    while True:
        if track_map[i][j] == 0: # delete
            todo_str.insert(0, 'd')
            target_str.insert(0, '*')
            source_str.insert(0, source[i-1])
            i -= 1
        elif track_map[i][j] == 1: # sub
            todo_str.insert(0, 's')
            target_str.insert(0, target[j-1])
            source_str.insert(0, source[i-1])
            i, j = i-1, j-1
        else: # insert
            todo_str.insert(0, 'i')
            target_str.insert(0, target[j-1])
            source_str.insert(0, '*')
            j -= 1

        #print(i,j)
        if i == 1 and j == 1:
            break

    print(70 * "=")
    print(" ".join(source_str))
    print(" ".join(len(todo_str) * '|'))
    print(" ".join(target_str))

    for i in range(len(todo_str)):
        if todo_str[i] == 's' and source_str[i] == target_str[i]:
            todo_str[i] = ' '

    print(" ".join(todo_str))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default='intention')
    parser.add_argument('--tar', type=str, default='execution')

    src = parser.parse_args().src
    tar = parser.parse_args().tar

    minimum_edit_distance(tar, src)

if __name__ == '__main__':
    main()
