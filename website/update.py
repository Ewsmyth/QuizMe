from flask import Blueprint, jsonify, request
import subprocess
import json

update = Blueprint('update', __name__)

@update.route('/update', methods=['POST'])
def update_app():
    try:
        # Detect the currently running container for the image
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'ancestor=ghcr.io/ewsmyth/quizme:latest', '--format', '{{.Names}}'],
            check=True, text=True, capture_output=True
        )
        current_container_name = result.stdout.strip()

        # If no container is running, skip stopping and removing
        if current_container_name:
            # Stop and remove the existing container
            subprocess.run(['docker', 'rm', '-f', current_container_name], check=True)

        # Determine a new container name or reuse the old one
        new_container_name = current_container_name or 'quizme'

        # Start a new container with the updated image
        subprocess.run([
            'docker', 'run', '-d', '--name', new_container_name, '-p', '6678:6678',
            'ghcr.io/ewsmyth/quizme:latest'
        ], check=True)

        return jsonify({'status': 'success', 'message': f'Updated to the latest version. Container: {new_container_name}'}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
