import subprocess, sys
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
r="/usr/local/lib/python3.13/dist-packages/nvidia/cu13"
print(sh(f"cat {r}/bin/nvcc.profile"))
print(sh(f"ls {r}/nvvm 2>&1 | head; find {r} -name cicc"))
for p in ("nvidia-nvvm", "nvidia-cuda-nvvm", "nvidia-cuda-crt", "nvidia-cuda-cccl"):
    print(p, sh(f"{sys.executable} -m pip index versions {p} 2>/dev/null | head -2"))
