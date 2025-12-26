pipeline {
    agent any

    environment {
        POETRY = "/home/pi/.local/bin/poetry"
        APP_DIR = "/home/pi/code/discord-bot"
    }

    stages {
        stage('Update code') {
            steps {
                sh '''
                    cd $APP_DIR
                    git pull
                '''
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    cd $APP_DIR
                    $POETRY install --no-interaction --no-ansi
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
