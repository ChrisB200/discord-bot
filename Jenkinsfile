pipeline {
    agent any

    environment {
        POETRY = "/var/lib/jenkins/.local/bin/poetry"
    }

    stages {
        stage('Deploy') {
            steps {
                sh '''
                    rsync -av --delete \
                      --exclude .git \
                      --exclude .venv \
                      --exclude .env \
                      . /home/pi/code/discord-bot/
                '''
            }
        }

        stage('Restart bot') {
            steps {
                sh '''
                    sudo systemctl restart discord-bot
                '''
            }
        }
    }
}
