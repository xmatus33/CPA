# This file contains parser of DPA v4.2 Contest database.
# (https://www.dpacontest.org/v4/42_traces.php)
#
# Traces from DPAv4.2 are divided into 16x2 subsets of 2,500 traces each.
# Index file is also present, holding metadata for all subsets.
# DPAv4.2 uses AES-128, thus keys are 16 byte long.
#
# Each line of Index file is structured as follows (columns separeted by spaces):
#   - 1st column: the AES-128 key (128 bits represented as 32 hexadecimal digits)
#   - 2nd column: the plaintext (128 bits represented as 32 hexadecimal digits)
#   - 3rd column: the ciphertext (128 bits represented as 32 hexadecimal digits)
#   - 4th column: the Shuffle0 permutation (see the algorithm specifications, 16 x 1 hexadecimal digit)
#   - 5th column: the Shuffle10 permutation (see the algorithm specifications, 16 x 1 hexadecimal digit)
#   - 6th column: the offsets (see the algorithm specifications, 16 x 1 hexadecimal digit)
#   - 7th column: the name of the directory (below the top-level directory DPA_contestv4_2) where the trace is stored
#   - 8th column: the name of the trace


import os
import numpy as np


def load_traces(path_to_folder, num_traces = None):
    '''Load traces'''

    traces = []

    print(f'Loading traces from: {os.path.abspath(path_to_folder)}')

    for file in list(os.listdir(path_to_folder)):

        file_path = os.path.join(path_to_folder, file)

        with open(file_path, 'rb') as trace_file:

            data = trace_file.read()[357:]    # Taking 1704462B with 357 byte offset
            data = np.array(list(data), dtype='int8')
            traces.append(data)
        
        if num_traces:
            if len(traces) >= num_traces:
                break
    
    print("Traces loaded.")

    return np.array(traces)


def parse_index_file(path_to_index_file, num_traces=300):
    """
    Parse the Index file of DPAv4.2 Contest Database.

    Takes path to Index file as parameter.

    Returns dictionary of parsed attributes (metadata) of Index file.
    Hexadecimal values are parsed as numpy array of uint8.
    """

    keys: list = []
    plaintexts: list = []
    ciphertexts: list = []
    shuffle0: list = []
    shuffle10: list = []
    offsets: list = []
    directory_names: list = []
    trace_names: list = []

    # Load index file for read only
    with open(path_to_index_file, "r") as index_file:

        num_loaded_traces = 0

        # Iterate over lines
        for line in index_file:

            # Parse one line

            if num_loaded_traces >= num_traces:
                break

            columns = line.split(" ")
            keys.append(list(bytes.fromhex(columns[0])))
            plaintexts.append(list(bytes.fromhex(columns[1])))
            ciphertexts.append(list(bytes.fromhex(columns[2])))
            shuffle0.append(list(bytes.fromhex(columns[3])))
            shuffle10.append(list(bytes.fromhex(columns[4])))
            
            # Parse offsets by 4-bit
            record = []
            for i in range(len(columns[5])):
                record.append(int(columns[5][i], 16))
                
            offsets.append(record)
            
            directory_names.append(columns[6][:-1])  # [:-1] cuts of '\n' at the end
            trace_names.append(columns[7][:-1])  # [:-1] cuts of '\n' at the end
            
            num_loaded_traces += 1

    # Return parsed index file
    return {
        "keys": np.array(keys, dtype='uint8'),
        "plaintexts": np.array(plaintexts, dtype='uint8'),
        "ciphertexts": np.array(ciphertexts, dtype='uint8'),
        "shuffle0": np.array(shuffle0, dtype='uint8'),
        "shuffle10": np.array(shuffle10, dtype='uint8'),
        "offsets": np.array(offsets, dtype='uint8'),
        "diretory_names": np.array(directory_names),
        "trace_names": np.array(trace_names),
    }
