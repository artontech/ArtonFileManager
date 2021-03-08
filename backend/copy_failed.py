import shutil
import os
target_dir = os.path.abspath('./failed_file')
os.makedirs(target_dir, exist_ok=True)
with open('failed_file.log', 'r') as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    fn = os.path.basename(line)
    print(line)
    target = os.path.join(target_dir, fn)
    shutil.copyfile(line, target)