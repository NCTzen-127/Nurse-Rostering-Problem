#导入库
from __future__ import division
from __future__ import print_function
import random
import copy

#数据
ability_nurses = [[0, 1, 2], [3, 2, 1], [1, 3, 2], [1, 2, 3], [2, 3, 1], [3, 3, 3]]#护士在各班次的适应度
num_shifts = 4#班次
num_nurses = 6
num_days = 3
num_night_shift = 1#每个护士夜班最大数目
n_0 = 2#早班所需护士最少数目
n_1 = 2#午班所需护士最少数目
n_2 = 1#晚班所需护士最少数目
w_1 = 2#如果前一天是晚班第二天是早班则惩罚，适应度-2
w_2 = 3#连着两天不值班适应度+3
w_3 = 3#前一天早班后一天不值班适应度+3
w_4 = 3#前一天不值班后一天晚班适应度+3

#初始化全局变量
num_back_track = 0#回溯次数
max_back_track = 100000#最大回溯次数
all_nurses = range(num_nurses)#0~5
all_shifts = range(num_shifts)#0~3，0表示早班，1表示午班，2表示晚班，3表示不值班
all_days = range(num_days)#0~2
domain = {}
decision_variable = {}#决策变量
primary_solution = []#主要解


#输出函数
def print_solution(solution):
    for n in all_nurses:
        for d in all_days:
            print("%i" % solution[(n, d)], end=" ")#输出该护士当天班次
        print()
    print("Total ability = %i" % get_value(solution))#输出总适应度


#起始域和决策变量
def initiation():
    for n in all_nurses:
        for d in all_days:
            domain[(n, d)] = set(all_shifts)#[0,1,2,3]
            decision_variable[(n, d)] = -1


#从第1天开始获取护士“ n”的夜班次数1~d
def get_number_night_shift(n, d):
    sum_night_shift = 0
    for i in range(d):
        sum_night_shift = sum_night_shift + (1 if decision_variable[(n, i)] == 2 else 0)#当天为夜班，数目加一

    return sum_night_shift


#计算解决方案的适应度
def get_value(solution):
    sum_ability = 0
    for n in all_nurses:
        for d in all_days:
            working_shift = solution[(n, d)]
            if working_shift != 3:
                sum_ability = sum_ability + ability_nurses[n][working_shift]

            # 如果前一天是晚班第二天是早班则惩罚:
            if working_shift == 0 and (d > 0 and solution[(n, d - 1)] == 2):
                sum_ability = sum_ability - w_1

            # 连着两天不值班
            if working_shift == 3 and (d > 0 and solution[(n, d - 1)] == 3):
                sum_ability = sum_ability + w_2

            # 前一天早班后一天不值班
            if working_shift == 3 and (d > 0 and solution[(n, d - 1)] == 0):
                sum_ability = sum_ability + w_3

            # 前一天不值班后一天晚班
            if working_shift == 2 and (d > 0 and solution[(n, d - 1)] == 3):
                sum_ability = sum_ability + w_4

    return sum_ability


'''
每天检查约束的最低护士人数
n_0 = 2#早班所需护士最少数目
n_1 = 2#午班所需护士最少数目
n_2 = 1#晚班所需护士最少数目
'''
def check_minimum_nurses_required(value_checking):
    for d in all_days:
        nurse_morning_shift = 0
        nurse_afternoon_shift = 0
        nurse_night_shift = 0

        for n in all_nurses:
            shift_type = value_checking[(n, d)]
            # 计算早午晚班护士数目
            if shift_type == 0:
                nurse_morning_shift += 1
            elif shift_type == 1:
                nurse_afternoon_shift += 1
            elif shift_type == 2:
                nurse_night_shift += 1

        if nurse_morning_shift < n_0 or nurse_afternoon_shift < n_1 or nurse_night_shift < n_2:
            return False

    return True


'''
向前检查方法，
如果找到满足约束条件的解决方案就存入primary_solution并返回1
否则返回2
'''
def check_forward(n, d):
    global num_back_track

    value_random = random.sample(domain[(n, d)], 1)[0]#随机选一个班次
    #如果当天值班且该护士该班次适应度为零
    if value_random != 3 and ability_nurses[n][value_random] == 0:
        num_back_track = num_back_track + 1
        return 2
    #该护士该日之前所值的夜班数加上当天夜班大于1
    if get_number_night_shift(n, d) + (1 if value_random == 2 else 0) > num_night_shift:
        num_back_track = num_back_track + 1
        return 2

    decision_variable[(n, d)] = value_random#决策变量等于值班班次

    if n == num_nurses - 1 and d == num_days - 1:#如果是最后一个护士的最后一天
        if check_minimum_nurses_required(decision_variable):#如果满足每个班次人数
            primary_solution.append(copy.deepcopy(decision_variable))#将该排班加入解决方案
            return 1
        #否则
        num_back_track = num_back_track + 1
        return 2

    next_day = (d + 1) % num_days
    next_nurse = n + (1 if next_day % num_days == 0 else 0)
    decision = check_forward(next_nurse, next_day)

    if decision != 0:
        return decision

    decision_variable[(n, d)] = -1#恢复决策变量

    num_back_track = num_back_track + 1
    if num_back_track >= max_back_track:
        return 2

    return 0


#禁忌搜索局部调整
def tabu_search(current_solution):
    result = current_solution.copy()
    best = get_value(current_solution)#适应度
    #局部交换计算适应度，找出局部最优解
    for d in all_days:
        for i in all_nurses:
            for k in all_nurses:
                if i != k:
                    current_decision_variable = copy.deepcopy(result)
                    current_decision_variable[(i, d)], current_decision_variable[(k, d)] = current_decision_variable[(k, d)], current_decision_variable[(i, d)]
                    if check_minimum_nurses_required(current_decision_variable):
                        current_value = get_value(current_decision_variable)
                        if current_value > best:
                            best = current_value
                            result = current_decision_variable.copy()

    return result


def main():
    # 初始化
    initiation()
    global domain
    # FC_CBJ多元约束算法，不断找出符合条件的解，直到回溯次数达到最大
    domain_backup = domain.copy()
    while num_back_track < max_back_track:
        decision = check_forward(0, 0)
        if decision == 2:
            domain = copy.deepcopy(domain_backup)

    print_solution(primary_solution[0])
    #找出局部最优解
    for i in range(0, len(primary_solution)):
        primary_solution[i] = tabu_search(primary_solution[i])

    print_solution(primary_solution[0])


if __name__ == '__main__':
    main()
