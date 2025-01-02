from common import *

queuing_latency = []
service_latency = []

for app in applications:
    queuing_latency.append(-1)
    service_latency.append(-1)

    for line in open('../pim_frfcfs/single_apps/' + app + '_nop'):
        if 'avg_mrq_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            queuing_latency[-1] = round(float(tokens[2]))
        elif 'avg_dram_service_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            service_latency[-1] = round(float(tokens[2]))

for pim in pim_kernels:
    queuing_latency.append(-1)
    service_latency.append(-1)

    filename = base_pim_files[pim] if pim in base_pim_files else pim + '_256'

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
        if 'avg_mrq_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            queuing_latency[-1] = round(float(tokens[2]))
        elif 'avg_dram_service_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            service_latency[-1] = round(float(tokens[2]))

# print applications
print('App', end='')
for i in range(len(applications)): print(',G' + str(i + 1), end='')
for i in range(len(pim_kernels)):  print(',P' + str(i + 1), end='')
print()

# print queuing latency
print('Queue', end='')
for i in range(len(applications)): print(',' + str(queuing_latency[i]), end='')
for i in range(len(pim_kernels)):
    index = len(applications) + i
    print(',' + str(queuing_latency[index]), end='')
print()

# print service latency
print('Service', end='')
for i in range(len(applications)): print(',' + str(service_latency[i]), end='')
for i in range(len(pim_kernels)):
    index = len(applications) + i
    print(',' + str(service_latency[index]), end='')
print()

# print percent queuing latency
print('Total', end='')
for i in range(len(applications)):
    print(',' + str(queuing_latency[i] + service_latency[i]), end='')
for i in range(len(pim_kernels)):
    index = len(applications) + i
    print(',' + str(queuing_latency[index] + service_latency[index]), end='')
print()
