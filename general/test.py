from sys import stdout

test_master_file = list(open('data/test-all-spells.txt', 'r'))
master_file = list(open('data/all-spells.txt', 'r'))
if len(test_master_file) != len(master_file):
    print "Mismatch file length"

if len(test_master_file) < len(master_file):
    file_lines = len(test_master_file)
else:
    file_lines = len(master_file)
line_count = 0
for x in range(file_lines):
    line_count += 1
    per = line_count / float(file_lines) * 100
    #stdout.write("Checking against master list: %d%%" % per)
    #stdout.flush()
    if test_master_file[x] != master_file[x]:
        print "MISMATCH! On line %s" % x
print " COMPLETE!"