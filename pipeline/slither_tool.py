import os
import subprocess


def analyze_slither(file_path: str) -> int:
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--platform",
                "linux/amd64",
                "-v",
                f"{os.getcwd()}:/contracts",
                "trailofbits/slither",
                "slither",
                f"/contracts/{file_path}",
            ],
            capture_output=True,
            text=True,
        )
        output = (result.stdout or "").lower()

        keywords = [
            "reentrancy",
            "overflow",
            "timestamp",
            "unchecked",
            "access control",
        ]

        return int(any(k in output for k in keywords))

    except Exception:
        return -1
