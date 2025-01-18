from flask import Blueprint, jsonify
import subprocess
import time

update = Blueprint('update', __name__)

@update.route('/update', methods=['POST'])
def update_app():
    try:
        print("Pulling the latest Docker image...")
        subprocess.run(['docker', 'pull', 'ghcr.io/ewsmyth/quizme:latest'], check=True)

        print("Fetching the currently running container...")
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'ancestor=ghcr.io/ewsmyth/quizme:latest', '--format', '{{.Names}}'],
            check=True, text=True, capture_output=True
        )
        current_container_name = result.stdout.strip()

        if current_container_name:
            print(f"Stopping and removing container: {current_container_name}")
            subprocess.run(['docker', 'rm', '-f', current_container_name], check=True)

        time.sleep(2)

        print("Checking port 6678 for conflicts...")
        check_port = subprocess.run(['lsof', '-i:6678'], capture_output=True, text=True)
        if check_port.stdout:
            print("Port 6678 is in use. Cleaning up...")
            lines = check_port.stdout.strip().split('\n')
            for line in lines:
                port_process = line.split()[1]
                subprocess.run(['kill', '-9', port_process], check=True)

        time.sleep(1)

        print("Cleaning up stopped containers...")
        subprocess.run(['docker', 'container', 'prune', '-f'], check=True)

        new_container_name = current_container_name or 'quizme'
        print(f"Starting new container: {new_container_name}")
        run_command = [
            'docker', 'run', '-d', '--name', new_container_name,
            '-p', '6678:6678', '-v', '/var/run/docker.sock:/var/run/docker.sock',
            'ghcr.io/ewsmyth/quizme:latest'
        ]
        print("Running command:", " ".join(run_command))
        subprocess.run(run_command, check=True)

        return jsonify({'status': 'success', 'message': f'Updated and started container: {new_container_name}'}), 200

    except subprocess.CalledProcessError as e:
        error_message = f"Command '{e.cmd}' failed with error: {e.stderr or e.output}"
        print(error_message)
        return jsonify({'status': 'error', 'message': error_message}), 500
