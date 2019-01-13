from __future__ import division
from __future__ import print_function
import random
import copy
import timeit

ability_nurses = [[0, 1, 2], [3, 2, 1], [1, 3, 2], [1, 2, 3], [2, 3, 1], [3, 3, 3]]
num_shifts = 4
num_nurses = 6
num_days = 3
max_num_night_shift = 1
n_0 = 2
n_1 = 2
n_2 = 1
w_1 = 2
w_2 = 3
w_3 = 3
w_4 = 3
num_back_track = 0
max_back_track = 50000
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)
domain = {}
decision_variable = {}
primary_solution = []


def print_solution(solution):
    for n in all_nurses:
        for d in all_days:
            print("%i" % solution[(n, d)], end=" ")
        print()
    print("Total ability = %i" % get_value(solution))


def initiation():
    for n in all_nurses:
        for d in all_days:
            domain[(n, d)] = set(all_shifts)
            decision_variable[(n, d)] = -1


def get_number_night_shift(n, d, decision_variable):
    sum_night_shift = 0
    for i in range(d):
        sum_night_shift = sum_night_shift + (1 if decision_variable[(n, i)] == 2 else 0)

    return sum_night_shift


def get_value(solution):
    sum_ability = 0
    for n in all_nurses:
        for d in all_days:
            working_shift = solution[(n, d)]
            if working_shift != 3:
                sum_ability = sum_ability + ability_nurses[n][working_shift]

            # penalty for night -> morning:
            if working_shift == 0 and (d > 0 and solution[(n, d - 1)] == 2):
                sum_ability = sum_ability - w_1

            # bonus for free free
            if working_shift == 3 and (d > 0 and solution[(n, d - 1)] == 3):
                sum_ability = sum_ability + w_2

            # morning free
            if working_shift == 3 and (d > 0 and solution[(n, d - 1)] == 0):
                sum_ability = sum_ability + w_3

            # free night
            if working_shift == 2 and (d > 0 and solution[(n, d - 1)] == 3):
                sum_ability = sum_ability + w_4

    return sum_ability


def check_minimum_nurses_required(value_checking):
    for d in all_days:
        nurse_morning_shift = 0
        nurse_afternoon_shift = 0
        nurse_night_shift = 0

        for n in all_nurses:
            shift_type = value_checking[(n, d)]
            # sum morning shift
            if shift_type == 0:
                nurse_morning_shift += 1
            elif shift_type == 1:
                nurse_afternoon_shift += 1
            elif shift_type == 2:
                nurse_night_shift += 1

        if nurse_morning_shift < n_0 or nurse_afternoon_shift < n_1 or nurse_night_shift < n_2:
            return False

    return True


def non_binary_checking_cp(n, d):
    domain_copy = copy.deepcopy(domain)
    current_number_night_shift = get_number_night_shift(n, d)
    for i in range(d + 1, num_days):
        for s in domain[(n, i)]:
            if current_number_night_shift + (1 if s == 2 else 0) > max_num_night_shift:
                domain_copy[(n, i)].remove(s)

            if not domain_copy[(n, i)]:
                return False

    return True


def check_forward(n, d):
    global num_back_track

    value_random = random.sample(domain[(n, d)], 1)[0]

    if value_random != 3 and ability_nurses[n][value_random] == 0:
        num_back_track = num_back_track + 1
        return 2

    if get_number_night_shift(n, d, decision_variable) + (1 if value_random == 2 else 0) > max_num_night_shift:
        num_back_track = num_back_track + 1
        return 2

    decision_variable[(n, d)] = value_random

    if n == num_nurses - 1 and d == num_days - 1:
        if check_minimum_nurses_required(decision_variable):
            primary_solution.append(copy.deepcopy(decision_variable))
            return 1

        num_back_track = num_back_track + 1
        return 2

    next_day = (d + 1) % num_days
    next_nurse = n + (1 if next_day % num_days == 0 else 0)
    decision = check_forward(next_nurse, next_day)
    if decision != 0:
        return decision

    decision_variable[(n, d)] = -1

    num_back_track = num_back_track + 1
    if num_back_track >= max_back_track:
        return 2

    return 0


def check_number_night_shift(current_decision_variable):
    for i in all_nurses:
        if get_number_night_shift(i, num_days, current_decision_variable) > max_num_night_shift:
            return False

    return True


def tabu_search(current_solution):
    result = current_solution.copy()
    best = get_value(current_solution)

    for d in all_days:
        for i in all_nurses:
            for k in all_nurses:
                if i != k:
                    current_decision_variable = copy.deepcopy(result)
                    current_decision_variable[(i, d)], current_decision_variable[(k, d)] = current_decision_variable[(k, d)], current_decision_variable[(i, d)]
                    if check_minimum_nurses_required(current_decision_variable) and check_number_night_shift(current_decision_variable):
                        current_value = get_value(current_decision_variable)
                        if current_value > best:
                            best = current_value
                            result = current_decision_variable.copy()

    return result


def main():
    # initiation
    initiation()
    global domain
    # FC_CBJ_NONBINARY_CP
    domain_backup = domain.copy()
    while num_back_track < max_back_track:
        decision = check_forward(0, 0)
        if decision == 2:
            domain = copy.deepcopy(domain_backup)

    result = tabu_search(primary_solution[0])
    best = get_value(result)
    for i in range(1, len(primary_solution)):
        primary_solution[i] = tabu_search(primary_solution[i])
        current = get_value((primary_solution[i]))
        if best < current:
            best = current
            result = primary_solution[i].copy()

    print_solution(result)


if __name__ == '__main__':
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print('Time: ', stop - start)
