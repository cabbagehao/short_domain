import subprocess
import time
from loguru import logger

prev_length = -1
t1 = time.time()
for i in range(1000):
        result = subprocess.run(["whois", f"notion{i}.so"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        length = len(output)
        t2 = time.time()
        logger.info(i, length, int(i / (t2 - t1)))
        # if prev_length != -1 and length != prev_length:
        if 'No Object Found' not in output:
            logger.info(f"new output: {output}")
            break
        prev_length = length