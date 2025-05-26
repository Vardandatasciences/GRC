import subprocess

def generate_prompt(length):
    # Generate a string of 'A's of specified length
    return "A" * length

def run_ollama(prompt):
    try:
        print(f"Running ollama with prompt length: {len(prompt)}")
        result = subprocess.run(
            ['ollama', 'run', 'mistral:7b-instruct', prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )
        stdout = result.stdout.decode('utf-8', errors='ignore')
        stderr = result.stderr.decode('utf-8', errors='ignore')
        print(f"Stdout length: {len(stdout)}")
        print(f"Stderr length: {len(stderr)}")
        return stdout, stderr
    except subprocess.TimeoutExpired:
        return None, "Timeout expired"
    except Exception as e:
        return None, str(e)


def main():
    low = 6000       # starting prompt length (characters)
    high = 16000     # max prompt length
    step = 500       # increment step size

    print("Starting empirical token limit test...")

    for length in range(low, high + 1, step):
        prompt = generate_prompt(length)
        print(f"Testing prompt length: {length} characters...")

        output, error = run_ollama(prompt)

        if error:
            print(f"Error at length {length}: {error}")
            break

        if output is None or output.strip() == "":
            print(f"No output returned at length {length}. Possibly limit reached or failure.")
            break

        # You can print or log output here if you want to verify
        # print(output)

        print(f"Success at length {length}")

    print("Test finished.")

if __name__ == "__main__":
    main()
