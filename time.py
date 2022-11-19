total_sum = 0
total_number = 0

user_sum = 0
sys_sum = 0

with open('time/time_768K.txt', 'r') as f:
    for line in f:
        try:
            num = float(line)
            total_sum += num

            if total_number % 2 == 0:
                user_sum += num
            else:
                sys_sum += num

            total_number += 1

        except ValueError:
            print('{} is not a number!'.format(line))


total_number /= 2
total_average = total_sum / total_number

print('Sum: {}'.format(total_sum))
print('Average: {}'.format(total_average))
print('user: {}'.format(user_sum / total_number))
print('sys: {}'.format(sys_sum/total_number))
