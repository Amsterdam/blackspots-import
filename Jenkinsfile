#!groovy
def PROJECT_NAME = "blackspots-backend"
def SLACK_CHANNEL = '#opdrachten-deployments'
def PLAYBOOK = 'deploy-blackspots.yml'
def SLACK_MESSAGE = [
    "title_link": BUILD_URL,
    "fields": [
        ["title": "Project","value": PROJECT_NAME],
        ["title":"Branch", "value": BRANCH_NAME, "short":true],
        ["title":"Build number", "value": BUILD_NUMBER, "short":true]
    ]
]



pipeline {
    agent any

    environment {
        SHORT_UUID = sh( script: "uuidgen | cut -d '-' -f1", returnStdout: true).trim()
        COMPOSE_PROJECT_NAME = "${PROJECT_NAME}-${env.SHORT_UUID}"
        VERSION = env.BRANCH_NAME.replace('/', '-').toLowerCase().replace(
            'master', 'latest'
        )
        IS_RELEASE = "${env.BRANCH_NAME ==~ "release/.*"}"
    }

    stages {
        stage('Test') {
            steps {
                sh 'make test'
            }
        }

        stage('Build') {
            steps {
                sh 'make build'
            }
        }

        stage('Push and deploy') {
            when { 
                anyOf {
                    branch 'master'
                    buildingTag()
                    environment name: 'IS_RELEASE', value: 'true'
                }
            }
            stages {
                stage('Push') {
                    steps {
                        script {
                            docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                                sh 'make push'
                            }
                        }
                    }
                }

                stage('Deploy to acceptance') {
                    when { environment name: 'IS_RELEASE', value: 'true' }
                    steps {
                        build job: 'Subtask_Openstack_Playbook', parameters: [
                            string(name: 'PLAYBOOK', value: PLAYBOOK),
                            string(name: 'INVENTORY', value: "acceptance"),
                            string(
                                name: 'PLAYBOOKPARAMS', 
                                value: "-e deployversion=${VERSION}"
                            )
                        ], wait: true
                    }
                }

                stage('Deploy to production') {
                    when { tag pattern: "\\d+\\.\\d+\\.\\d+\\.*", comparator: "REGEXP" }
                    steps {
                        build job: 'Subtask_Openstack_Playbook', parameters: [
                            string(name: 'PLAYBOOK', value: PLAYBOOK),
                            string(name: 'INVENTORY', value: "production"),
                            string(
                                name: 'PLAYBOOKPARAMS', 
                                value: "-e deployversion=${VERSION}"
                            )
                        ], wait: true

                        slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE << 
                            [
                                "color": "#36a64f",
                                "title": "Deploy to production succeeded :rocket:",
                            ]
                        ])
                    }
                }
            }
        }

    }
    post {
        always {
            sh 'make clean'
        }
        failure {
            slackSend(channel: SLACK_CHANNEL, attachments: [SLACK_MESSAGE << 
                [
                    "color": "#D53030",
                    "title": "Build failed :fire:",
                ]
            ])
        }
    }
}
