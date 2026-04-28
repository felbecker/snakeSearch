# type: ignore
import os
import subprocess

TOOLS = config["tools"]
SAMPLES, = glob_wildcards(config["data_path"]+"/{sample}")

rule all:
    input:
        expand(
            "outputs/"+config["name"]+"/{tool}/search_out/{sample}",
            tool=TOOLS,
            sample=SAMPLES
        )


def run_tool(cmd, output_path, log_stdout, log_stderr, pipe_output=False):
    """Run a shell command, write logs, and mark the output as FAILED on error."""
    if pipe_output:
        cmd += " > " + output_path

    print("Running command: ", cmd)

    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = p.communicate()

    with open(log_stderr, "w") as err_file:
        print(stderr.decode(), file=err_file)

    with open(log_stdout, "w") as log_file:
        print(stdout.decode(), file=log_file)

    if not (
        os.path.exists(output_path)
        and p.returncode == 0
        and os.path.getsize(output_path) != 0
    ):
        with open(output_path, "w") as fout:
            fout.write("FAILED")


def parse_cmd_args(params):
    return " ".join(params)


include: "rules/build_hmm"
include: "rules/search"
