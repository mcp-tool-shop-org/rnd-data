import subprocess, sys
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
print(sh(f"{sys.executable} -m pip show nvidia-cuda-nvcc 2>&1 | head -3"))
print(sh(f"{sys.executable} -m pip index versions nvidia-cuda-nvcc 2>&1 | head -3"))
print(sh("python -c 'import nvidia, os; print(nvidia.__path__)'"))
print(sh("find / -name nvcc -type f 2>/dev/null | head -10"))
print(sh("ls /usr/local/ | grep -i cuda"))
