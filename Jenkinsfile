pipeline {
    agent any

    environment {
        POETRY = "/home/pi/.local/bin/poetry"
    }

    stages {
        stage('Install dependencies') {
            steps {
                sh '''
                    $POETRY install --no-interaction --no-ansi
                '''
            }
        }

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
