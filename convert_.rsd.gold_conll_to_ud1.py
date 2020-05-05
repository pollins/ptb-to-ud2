# Note that this converts to UD1, UD2 to be implemented
# For now use "udapy -s ud.Convert1to2 < ud1.conllu > ud2.conllu" to convert this output to UD2

from argparse import ArgumentParser
import subprocess, shlex

stanford_path = './stanford-parser-full-2018-10-17/*'

text = 'Converts .rsd.gold_conll file to Universal Dependencies v1'

parser = ArgumentParser(description = text)
parser.add_argument('files', metavar = 'file', type = str, nargs = '+', help = 'Source file(s)')
parser.add_argument('--stanford_path', help = 'Stanford parser path (default is %s)' % stanford_path)

args = parser.parse_args()

if args.stanford_path:
    stanford_path = args.stanford_path

for in_filename in args.files:
	tree_filename = in_filename + '.treebank'

	in_file = open(in_filename)
	tree_file = open(tree_filename, 'w+')

	for line in in_file:
	    line = line.strip() # need to change all newlines to whitespace
	    if line and (line[0] != '#'): # ignore commented lines
	        words = line.split()[3:6]
	        # words[0] is the constituent token, words[1] is the constituent label, and words[2] is parent labels
	        before, after = words[2].split('*') # * indicates constituent token place
	        tree_file.write('%s(%s %s)%s\n' % (before, words[1], words[0], after))
	    else:
	        tree_file.write('\n')

	in_file.close()
	tree_file.close()

command = 'java -cp \"%s\" -mx1g edu.stanford.nlp.trees.ud.UniversalDependenciesConverter -treeFile ./%s' % (stanford_path, tree_filename)

proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(proc.communicate()[0].decode('utf-8'))
subprocess.call(['rm', tree_filename])
