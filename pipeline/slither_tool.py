import json
import tempfile
import subprocess

def analyze_slither(file_path, vuln_type):

    detectors = DETECTOR_MAP.get(vuln_type, [])

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".json",
            delete=False
        ) as tmp:

            json_file = tmp.name

        cmd = [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{os.getcwd()}:/contracts",
            "trailofbits/slither",
            "slither",
            f"/contracts/{file_path}",
            "--detect",
            ",".join(detectors),
            "--json",
            f"/contracts/{json_file}"
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        with open(json_file, "r") as f:

            data = json.load(f)

        findings = data.get("results", {}).get("detectors", [])

        return 1 if len(findings) > 0 else 0

    except Exception as e:

        print("SLITHER ERROR:", e)

        return -1