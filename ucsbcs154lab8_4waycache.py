# ucsbcs154lab8_4waycache.py
# All Rights Reserved
# Copyright (c) 2022 Jonathan Balkind
# Distribution Prohibited

import pyrtl

pyrtl.core.set_debug_mode()

# Cache parameters:
# 32 bit addresses
# 4 ways
# 16 rows
# 16 bytes (4 words) per block

# Inputs
req_new = pyrtl.Input(bitwidth=1, name='req_new')       # High on cycles when a request is occurring
req_addr = pyrtl.Input(bitwidth=32, name='req_addr')    # Requested address
req_type = pyrtl.Input(bitwidth=1, name='req_type')     # 0 read, 1 write
req_data = pyrtl.Input(bitwidth=32, name='req_data')    # Only for writes

# Outputs
resp_hit = pyrtl.Output(bitwidth=1, name='resp_hit')    # Indicates whether there was a cache hit
resp_data = pyrtl.Output(bitwidth=32, name='resp_data') # If read request, return data at req_addr

# Memories
valid_0 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_0')
valid_1 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_1')
valid_2 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_2')
valid_3 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_3')

tag_0 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_0')
tag_1 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_1')
tag_2 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_2')
tag_3 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=3, asynchronous=True, name='tag_3')

data_0 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_0')
data_1 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_1')
data_2 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_2')
data_3 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_3')

# To track which Way entry to replace next.
repl_way = pyrtl.MemBlock(bitwidth=2, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='repl_way')

# TODO: Declare your own WireVectors, MemBlocks, etc.

offset = pyrtl.WireVector(bitwidth=4, name="offset")
index = pyrtl.WireVector(bitwidth=4, name="index")
tag = pyrtl.WireVector(bitwidth=24, name="tag")

offset <<= req_addr[0:4]
index <<= req_addr[4:8]
tag <<= req_addr[8:32]

####################################################################################

# TODO: Check four entries in a row in parallel.

# entry_0_tag = pyrtl.WireVector(bitwidth=24, name="entry_0_tag")
# entry_1_tag = pyrtl.WireVector(bitwidth=24, name="entry_1_tag")
# entry_2_tag = pyrtl.WireVector(bitwidth=24, name="entry_2_tag")
# entry_3_tag = pyrtl.WireVector(bitwidth=24, name="entry_3_tag")

entry_0_valid = pyrtl.WireVector(bitwidth=1, name="entry_0_valid")
entry_1_valid = pyrtl.WireVector(bitwidth=1, name="entry_1_valid")
entry_2_valid = pyrtl.WireVector(bitwidth=1, name="entry_2_valid")
entry_3_valid = pyrtl.WireVector(bitwidth=1, name="entry_3_valid")

# entry_0_tag <<= tag_0[index]
# entry_1_tag <<= tag_1[index]
# entry_2_tag <<= tag_2[index]
# entry_3_tag <<= tag_3[index]

entry_0_valid <<= valid_0[index]
entry_1_valid <<= valid_1[index]
entry_2_valid <<= valid_2[index]
entry_3_valid <<= valid_3[index]

hit_block = pyrtl.WireVector(bitwidth=3, name="hit_block")

with pyrtl.conditional_assignment:
    with tag == tag_0[index]:
        with entry_0_valid == 1:
            hit_block |= 0
    with tag == tag_1[index]:
        with entry_1_valid == 1:
            hit_block |= 1
    with tag == tag_2[index]:
        with entry_2_valid == 1:
            hit_block |= 2
    with tag == tag_3[index]:
        with entry_3_valid == 1:
            hit_block |= 3
    with pyrtl.otherwise:
        hit_block |= 5



repl_val = pyrtl.WireVector(bitwidth=2, name="repl_val")
repl_val <<= repl_way[index]

# TODO: Determine if hit or miss.
hit_result = pyrtl.WireVector(bitwidth=1, name="hit_result")
with pyrtl.conditional_assignment:
    with hit_block == 5:
        hit_result |= 0
    with pyrtl.otherwise:
        hit_result |= 1

# TODO: If request type is write, write req_data to appropriate block address
enable_0 = pyrtl.WireVector(bitwidth=1, name="enable_0")
enable_1 = pyrtl.WireVector(bitwidth=1, name="enable_1")
enable_2 = pyrtl.WireVector(bitwidth=1, name="enable_2")
enable_3 = pyrtl.WireVector(bitwidth=1, name="enable_3")

# set enables
with pyrtl.conditional_assignment:
    with ((hit_block == 0) & (req_new == 1) & (req_type == 1) & (hit_result == 1)) :
        enable_0 |= 1
        enable_1 |= 0
        enable_2 |= 0
        enable_3 |= 0
    with hit_block == 1 & (req_new == 1) & (req_type == 1):
        enable_0 |= 0
        enable_1 |= 1
        enable_2 |= 0
        enable_3 |= 0
    with hit_block == 2 & (req_new == 1) & (req_type == 1):
        enable_0 |= 0
        enable_1 |= 0
        enable_2 |= 1
        enable_3 |= 0
    with hit_block == 3 & (req_new == 1) & (req_type == 1):
        enable_0 |= 0
        enable_1 |= 0
        enable_2 |= 0
        enable_3 |= 1
    with hit_block == 5 & (req_new == 1) & (req_type == 1):
        with repl_val == 0:
            enable_0 |= 1
            enable_1 |= 0
            enable_2 |= 0
            enable_3 |= 0
        with repl_val == 1:
            enable_0 |= 0
            enable_1 |= 1
            enable_2 |= 0
            enable_3 |= 0
        with repl_val == 2:
            enable_0 |= 0
            enable_1 |= 0
            enable_2 |= 1
            enable_3 |= 0
        with repl_val == 3:
            enable_0 |= 0
            enable_1 |= 0
            enable_2 |= 0
            enable_3 |= 1


data_shift_amount = pyrtl.WireVector(bitwidth=128, name="data_shift_amount")

# set shift amount
with pyrtl.conditional_assignment:
    with offset == 0b0000:
        data_shift_amount |= offset*8
    with offset == 0b0100:
        data_shift_amount |= offset*8
    with offset == 0b1000:
        data_shift_amount |= offset*8
    with offset == 0b1100:
        data_shift_amount |= offset*8


write_mask = pyrtl.WireVector(bitwidth=128, name="write_mask")
write_data = pyrtl.WireVector(bitwidth=128, name="write_data")

write_mask <<= pyrtl.select(hit_result, ~pyrtl.shift_left_logical(pyrtl.Const(0x0ffffffff, bitwidth=128), data_shift_amount), 0)
write_data <<= pyrtl.shift_left_logical(req_data.zero_extended(bitwidth=128), data_shift_amount)

data_0_payload = pyrtl.WireVector(bitwidth=128, name="data_0_payload")
data_0_payload <<= data_0[index]

data_1_payload = pyrtl.WireVector(bitwidth=128, name="data_1_payload")
data_1_payload <<= data_1[index]

data_2_payload = pyrtl.WireVector(bitwidth=128, name="data_2_payload")
data_2_payload <<= data_2[index]

data_3_payload = pyrtl.WireVector(bitwidth=128, name="data_3_payload")
data_3_payload <<= data_3[index]



data_0[index] <<= pyrtl.MemBlock.EnabledWrite((data_0_payload & write_mask) | write_data, enable_0) 
data_1[index] <<= pyrtl.MemBlock.EnabledWrite((data_1_payload & write_mask) | write_data, enable_1)
data_2[index] <<= pyrtl.MemBlock.EnabledWrite((data_2_payload & write_mask) | write_data, enable_2)
data_3[index] <<= pyrtl.MemBlock.EnabledWrite((data_3_payload & write_mask) | write_data, enable_3)


new_repl_val = pyrtl.WireVector(bitwidth=2, name="new_repl_val")

new_data_0 = pyrtl.WireVector(bitwidth=128, name="new_data_0")
new_data_1 = pyrtl.WireVector(bitwidth=128, name="new_data_1")
new_data_2 = pyrtl.WireVector(bitwidth=128, name="new_data_2")
new_data_3 = pyrtl.WireVector(bitwidth=128, name="new_data_3")

new_valid_0 = pyrtl.WireVector(bitwidth=1, name="new_valid_0")
new_valid_1 = pyrtl.WireVector(bitwidth=1, name="new_valid_1")
new_valid_2 = pyrtl.WireVector(bitwidth=1, name="new_valid_2")
new_valid_3 = pyrtl.WireVector(bitwidth=1, name="new_valid_3")

new_tag_0 = pyrtl.WireVector(bitwidth=24, name="new_tag_0")
new_tag_1 = pyrtl.WireVector(bitwidth=24, name="new_tag_1")
new_tag_2 = pyrtl.WireVector(bitwidth=24, name="new_tag_2")
new_tag_3 = pyrtl.WireVector(bitwidth=24, name="new_tag_3")



# round robin
with pyrtl.conditional_assignment:
    with repl_val == 3:
        new_repl_val |= 0
    with pyrtl.otherwise:
        new_repl_val |= repl_val + 1

# read hit
with pyrtl.conditional_assignment:
    with (req_new == 1) & (req_type == 0) & (hit_block == 0):
        resp_hit |= 1
        resp_data|= pyrtl.shift_right_logical(data_0_payload, data_shift_amount)
    with (req_new == 1) & (req_type == 0) & (hit_block == 1):
        resp_hit |= 1
        resp_data|= pyrtl.shift_right_logical(data_1_payload, data_shift_amount)
    with (req_new == 1) & (req_type == 0) & (hit_block == 2):
        resp_hit |= 1
        resp_data|= pyrtl.shift_right_logical(data_2_payload, data_shift_amount)
    with (req_new == 1) & (req_type == 0) & (hit_block == 3):
        resp_hit |= 1
        resp_data|= pyrtl.shift_right_logical(data_3_payload, data_shift_amount)


with pyrtl.conditional_assignment:
    with (req_new == 1) & (req_type == 0) & (hit_block == 5):
        resp_hit |= 0
        resp_data |= 0

# read miss
with pyrtl.conditional_assignment:
    with (req_new == 1) & (req_type == 0) & (hit_block == 5) & (repl_val == 0):
        repl_way[index] |= new_repl_val
        new_data_0 |= 0
        new_valid_0 |= 1
        new_tag_0 |= tag
    with (req_new == 1) & (req_type == 0) & (hit_block == 5) & (repl_val == 1):
        new_data_1 |= 0
        new_valid_1 |= 1
        new_tag_1 |= tag
    with (req_new == 1) & (req_type == 0) & (hit_block == 5) & (repl_val == 2):
        new_data_2 |= 0
        new_valid_2 |= 1
        new_tag_2 |= tag
    with (req_new == 1) & (req_type == 0) & (hit_block == 5) & (repl_val == 3):
        new_data_3 |= 0
        new_valid_3 |= 1
        new_tag_3 |= tag

#no action
with pyrtl.conditional_assignment:
    with (req_new == 0):
        resp_hit |= 0
        resp_data |= 0

#write hit
with pyrtl.conditional_assignment:
    with (req_new == 1) & (req_type == 1) & (hit_block != 5):
        resp_hit |= 1
        resp_data |= 0

#write miss
with pyrtl.conditional_assignment:
    with (req_new == 1) & (req_type == 1) & (hit_block == 5):
        resp_hit |= 0
        resp_data |= 0
        repl_way[index] |= new_repl_val
        with repl_val == 0:
            new_data_0 |= write_data
        with repl_val == 1:
            new_data_1 |= write_data
        with repl_val == 2:
            new_data_2 |= write_data
        with repl_val == 3:
            new_data_3 |= write_data

# TODO: Handle replacement. Be careful handling replacement when you
# also have to do a write



# TODO: Determine output

    

############################## SIMULATION ######################################
pyrtl.set_debug_mode(debug=True)

def TestNoRequest(simulation, trace, addr=1024):
    simulation.step({
        'req_new':0,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0)
    print("Passed No Request Case!")

# Precondition: addr is not already in the cache.
# Postcondition: There is a cache miss. 
def TestMiss(simulation, trace, addr = 0):
    simulation.step({
        'req_new':1,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0)

    print("Passed Miss Case!")

# Precondition: addr is already in the cache.
# Postcondition: There is a cache hit and the cache returns
# the expected word. 
def TestHit(simulation, trace, addr = 0, expected_data = 0):
    simulation.step({
        'req_new':1,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == expected_data) 

    print("Passed Hit Case!")

# Precondition: addr is already in the cache.
# Postcondition: The word located at memory address 'addr'
# has been replaced with 'new_data'.
def TestWrite(simulation, trace, addr=0, new_data=156):
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 1,
        'req_data': new_data,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == 0) 

    # Read back the correct value
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == new_data) 
    print("Passed Write Test!")

# Precondition: addr does not already hit in the cache.
# Postcondition: addr exists in the cache at the correct
# cache index
def TestCorrectIndex(simulation, trace, addr = 32):
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0) 

    bin_addr = bin(addr)[2:]
    missing_bits = 32 - len(bin_addr)
    if missing_bits > 0:
        bin_addr = ("0" * missing_bits) + bin_addr

    cache_index = int("0b" + bin_addr[-8:-4], 2)
    addr_tag = int("0b" + bin_addr[:24], 2)

    tag_0_val = float('inf') if cache_index not in simulation.inspect_mem(tag_0) else simulation.inspect_mem(tag_0)[cache_index]
    tag_1_val = float('inf') if cache_index not in simulation.inspect_mem(tag_1) else simulation.inspect_mem(tag_1)[cache_index]
    tag_2_val = float('inf') if cache_index not in simulation.inspect_mem(tag_2) else simulation.inspect_mem(tag_2)[cache_index]
    tag_3_val = float('inf') if cache_index not in simulation.inspect_mem(tag_3) else simulation.inspect_mem(tag_3)[cache_index]

    assert((tag_0_val == addr_tag) or (tag_1_val == addr_tag) or (tag_2_val == addr_tag) or (tag_3_val == addr_tag))

    # Ensure that we hit in the next cycle.
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == 0) 

    print("Passed Correct Index Test!")

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

TestNoRequest(sim, sim_trace)
TestMiss(sim, sim_trace)
TestHit(sim, sim_trace)
TestWrite(sim, sim_trace)
TestCorrectIndex(sim, sim_trace)

# Print trace
# sim_trace.render_trace(symbol_len=8)