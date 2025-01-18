from flask import Blueprint, jsonify
import subprocess
import time

update = Blueprint('update', __name__)

@update.route('/update', methods=['POST'])
def update_app():
    try:
        # Pull the latest Docker image
        subprocess.run(['docker', 'pull', 'ghcr.io/ewsmyth/quizme:latest'], check=True)

        # Get the name of the currently running container
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'ancestor=ghcr.io/ewsmyth/quizme:latest', '--format', '{{.Names}}'],
            check=True, text=True, capture_output=True
        )
        current_container_name = result.stdout.strip()

        # Stop and remove the existing container if it exists
        if current_container_name:
            subprocess.run(['docker', 'rm', '-f', current_container_name], check=True)

        # Wait for a short period to ensure the port is released
        time.sleep(2)

        # Check if the port is free
        check_port = subprocess.run(['lsof', '-i:6678'], capture_output=True, text=True)
        if check_port.stdout:
            # If the port is still in use, kill the process
            port_process = check_port.stdout.split()[1]
            subprocess.run(['kill', '-9', port_process], check=True)

        # Clean up stopped containers
        subprocess.run(['docker', 'container', 'prune', '-f'], check=True)

        # Start a new container
        new_container_name = current_container_name or 'quizme'
        run_command = [
            'docker', 'run', '-d', '--name', new_container_name,
            '-p', '6678:6678', '-v', '/var/run/docker.sock:/var/run/docker.sock',
            'ghcr.io/ewsmyth/quizme:latest'
        ]

        print("Running command:", " ".join(run_command))  # Debugging output
        subprocess.run(run_command, check=True)

        return jsonify({'status': 'success', 'message': f'Updated and started container: {new_container_name}'}), 200

    except subprocess.CalledProcessError as e:
        error_message = f"Command '{e.cmd}' failed with error: {e.stderr or e.output}"
        print(error_message)
        return jsonify({'status': 'error', 'message': error_message}), 500
