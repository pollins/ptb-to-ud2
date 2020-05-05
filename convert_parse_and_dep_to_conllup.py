# can be used as module for convert_all_thyme_files_to_conllup.py

from argparse import ArgumentParser
import subprocess, shlex

text = 'Given THYME directory with .parse (PTB) and .dep (Jinho\'s dependency conversion) files, outputs CoNLL-U Plus format. Requires Stanford Parser and udapi'
stanford_path = '../stanford-parser-full-2018-10-17/*'

parser = ArgumentParser(description = text)
parser.add_argument('dir', help = 'Source directory')
parser.add_argument('--stanford_path', help = 'Stanford parser path (default is %s)' % stanford_path)

args = parser.parse_args()

dir = args.dir
file_base_name = dir.split('/')[-1]
file_prefix = f'./{dir}/{file_base_name}'

if args.stanford_path:
    stanford_path = args.stanford_path

command = f'java -cp \"{stanford_path}\" -mx1g edu.stanford.nlp.trees.ud.UniversalDependenciesConverter -treeFile {file_prefix}.parse'
p1 = subprocess.Popen(shlex.split(command), stdout = subprocess.PIPE) # first, run the stanford parser
p2 = subprocess.Popen(shlex.split(f'udapy -s ud.Convert1to2'), stdin = p1.stdout, stdout = subprocess.PIPE) # take that output, and send to udapi, need to figure out how to call this module directly instead of through shell
p1.stdout.close()

ud2_lines = p2.communicate()[0].decode('utf8').split('\n')[:-1] # must split as lines and cut off last empty list
p2.stdout.close()

# combine this data with the .dep information

def get_data(lines):
    result = []
    sent = []
    for line in lines:
        if line:
            if line[0] != '#':
                line = line.strip().split()
            else:
                line = [line.strip()]

        if line:
            sent.append(line)
        else:
            result.append(sent)
            sent = []
    return result

dep = get_data(open(f'{file_prefix}.dep', encoding = 'utf8'))
ud2 = get_data(ud2_lines)


def get_pred_dict_and_label_dict(sent):

    pred_dict = {}
    col_dict = {}
    col = 12 # number of the first APRED column
    for line in dep[i]:

        roles = {}
        roles_str = line[4]
        if roles_str != '_':
            for element in roles_str.split('|'):
                key, value = element.split('=')
                roles[key] = value
            if 'pb' in roles:
                pred_dict[int(line[0])] = roles['pb']
                col_dict[int(line[0])] = col
                col += 1

    label_dict = {}
    for line in dep[i]:
        labels_str = line[8]
        if labels_str != '_':
            labels = {}
            for element in labels_str.split(';'):
                line_no_and_value = element.split(':')
                line_no = int(line_no_and_value[0])
                value = line_no_and_value[1]
                col = col_dict[line_no]
                labels[col] = value
            label_dict[int(line[0])] = labels

    return pred_dict, label_dict

for i, sent in enumerate(ud2):
    pred_dict, label_dict = get_pred_dict_and_label_dict(sent)
    new_cols = len(pred_dict) + 2

    for line in sent:
        if line[0][0] != '#':
            line += ['_'] * new_cols

    line_offset = 1

    for line_no, pred in pred_dict.items():
        index = line_no + line_offset
        sent[index][10] = 'Y'
        sent[index][11] = pred

    for line_no, labels in label_dict.items():
        index = line_no + line_offset
        for col_no, label in labels.items():
            sent[index][col_no] = label

    for q in sent:
        print('\t'.join(q))
    print()
print()
