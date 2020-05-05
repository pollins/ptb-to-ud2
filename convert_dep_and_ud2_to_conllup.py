from argparse import ArgumentParser

text = 'Outputs file in our CoNLL-U Plus format'

parser = ArgumentParser(description = text)
parser.add_argument('--ud2', help = 'Universal dependencies v2 file')
parser.add_argument('--jinho_dependency', help = 'Output file from Jinho Choi\'s script')

args = parser.parse_args()

def get_data(filename):
    result = []
    sent = []
    for line in open(filename, encoding = 'utf8'):
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

jinho = get_data(args.jinho_dependency)
ud2 = get_data(args.ud2)

def get_pred_dict_and_label_dict(sent):

    pred_dict = {}
    col_dict = {}
    col = 12 # number of the first APRED column
    for line in jinho[i]:

        roles = {}
        roles_str = line[4]
        if roles_str != '_':
            for element in roles_str.split('|'):
                key, value = element.split('=')
                roles[key] = value
            if 'pred' in roles:
                pred_dict[int(line[0])] = roles['pred']
                col_dict[int(line[0])] = col
                col += 1

    label_dict = {}
    for line in jinho[i]:
        labels_str = line[7]
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
