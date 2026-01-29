import subprocess
import json
import sys

def run_test():
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "-m", "lol_fandom_mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr, # Let stderr flow through to console for debugging
        cwd=r"c:\Users\jqueiroz\Documents\projeto",
        text=True,
        bufsize=0 # Unbuffered
    )

    try:
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"names": "test-client"}
        }
        print(f"Sending: {json.dumps(init_req)}")
        
        # Write line by line
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()

        response_line = process.stdout.readline()
        print(f"Received: {response_line}")
        response = json.loads(response_line)
        assert response["id"] == 1
        assert "serverInfo" in response["result"]

        # 2. Call Tool (search_wiki)
        tool_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_wiki",
                "arguments": {"query": "Ahri", "limit": 1}
            }
        }
        print(f"Sending: {json.dumps(tool_req)}")
        process.stdin.write(json.dumps(tool_req) + "\n")
        process.stdin.flush()

        response_line = process.stdout.readline()
        print(f"Received: {response_line}")
        response = json.loads(response_line)
        assert response["id"] == 2
        content = response["result"]["content"][0]["text"]
        print(f"Tool Result Content: {content}")
        assert "Ahri" in content

    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    run_test()
