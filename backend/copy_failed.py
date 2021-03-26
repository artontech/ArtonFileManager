import shutil
import os
target_dir = os.path.abspath('./failed_file')
os.makedirs(target_dir, exist_ok=True)
with open('failed_file.log', 'r') as f:
    lines = f.readlines()
remain = lines.copy()
count = len(lines)
for i in range(count):
    line = lines[i].strip()
    fn = os.path.basename(line)
    print("%d/%d %s" % (i, count, line))
    target = os.path.join(target_dir, fn)
    temp = target + ".lock"
    shutil.copyfile(line, temp)
    os.rename(temp, target)
    remain.remove(lines[i])
    with open('failed_file_remain.log', 'w+') as f:
        f.writelines(remain)