total_sum = 0
total_number = 0

with open('Benchmark/time.txt', 'r') as f:
    for line in f:
        try:
            num = float(line)
            total_sum += num
            total_number += 1
        except ValueError:
            print('{} is not a number!'.format(line))

total_number /= 2
average = total_sum / total_number

print('Sum: {}'.format(total_sum))
print('Average: {}'.format(average))
