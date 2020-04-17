import os

from src.shared.classes import Srl_info
# import sys
# for pack in os.listdir("src"):
#     sys.path.append(os.path.join("src", pack))
# sys.path.append("/src/shared/")
# from classes import *


def parse_swirl_sent(sent_id, sent_tokens):
    '''
    This function gets a sentence in a SwiRL "format" and extracts the predicates
    and their arguments from it.
    The function returns a dictionary in the following structure:
    dict[key3] = Srl_info object
    while key3 is a token id of an extracted event.
    See a documentation about Srl_info object in classed.py.
    :param sent_id: the sentence ordinal number in the document
    :param sent_tokens: the sentence's tokens
    :return: a dictionary as mentioned above
    '''
    col = 0
    event_dict = {}
    for tok_idx, tok in enumerate(sent_tokens):
        if tok[0] != '-':
            col += 1
            events_args = {}
            # look for the arguments
            for arg_idx, arg in enumerate(sent_tokens):
                if '(' in arg[col] and ')' in arg[col]:
                    # one word argument
                    arg_name = arg[col][1:-1]
                    arg_name = arg_name.replace('*','')
                    arg_name = arg_name.replace('R-', '')
                    events_args[arg_name] = [arg_idx]
                elif '(' in arg[col]:
                    # argument with two or more words
                    arg_bound_found = False
                    arg_name = arg[col][1:-1]
                    arg_name = arg_name.replace('*', '')
                    arg_name = arg_name.replace('R-', '')
                    events_args[arg_name] = [arg_idx]
                    bound_idx = arg_idx + 1
                    while bound_idx < len(sent_tokens) and not arg_bound_found:
                        if ')' in sent_tokens[bound_idx][col]:
                            events_args[arg_name].append(bound_idx)
                            arg_bound_found = True
                        bound_idx += 1
            # save the arguments per predicate
            event_dict[tok_idx] = Srl_info(sent_id, events_args,tok_idx, tok[0])
    return event_dict


def parse_swirl_file(xml_file_name, srl_file_path, srl_data):
    '''
    This function gets the path to a SwiRL output file,
    extracts the predicates and their arguments for each sentence in this document
    and returns a dictionary in the following structure:
    dict[key1][key2][key3] contains a Srl_info object.
    key1 - document id
    key2 - sent id
    key3 - token id of an extracted event

    :param xml_file_name: name of the input file of SwiRL, (name of the xml file in ecb+)
    :param srl_file_path: path to the output file of SwiRL
    :param srl_data: A dict that saves srl info of many files. The extracted srl
     info of this file will be save into this dict also.
    '''
    srl_file = open(srl_file_path, 'r')
    xml_file_mainname = xml_file_name.split('.')[0]
    srl_data[xml_file_mainname] = {}
    sent_id = 0
    sent_tokens = []
    for line in srl_file:
        temp_line = line.strip().split()
        if not temp_line:
            srl_data[xml_file_mainname][sent_id] = parse_swirl_sent(sent_id, sent_tokens)
            sent_id += 1
            sent_tokens = []
        else:
            sent_tokens.append(temp_line)
    # parse the last sentence
    srl_data[xml_file_mainname][sent_id] = parse_swirl_sent(sent_id, sent_tokens)
    srl_file.close()


def parse_swirl_output(srl_folder_path):
    '''
    This function gets the path to the output files of SwiRL and parse
    each output file

    :param srl_folder_path: the path to the folder which includes the output files of SwiRL
    :return: a dictionary (see the previous function's documentation)
    '''
    srl_data = {}
    srl_file_name_list = os.listdir(srl_folder_path)
    for srl_file_name in srl_file_name_list:
        srl_file_path = os.path.join(srl_folder_path, srl_file_name)
        splitted = srl_file_name.split('.')  # 'SWIRL_OUTPUT.10_13ecbplus.xml.txt'
        xml_file_name = splitted[1] + '.' + splitted[2]  # '10_13ecbplus.xml'

        parse_swirl_file(xml_file_name, srl_file_path, srl_data)

    return srl_data


