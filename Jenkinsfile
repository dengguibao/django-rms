pipeline {
    agent any
    options { 
        disableConcurrentBuilds() 
    }
    stages {
        stage ('pull code') {
            steps{
                // sh '''
                //     if [ -d ./dms ]; then
                //         rm -rf dms/
                //     fi
                //     git clone root@172.31.12.254:/django/dms.git
                //     '''
                checkout
            }
        }
        
        stage ('test') {
            agent {
                docker{
                    image "django-ops:latest"
                    args "-v ${env.WORKSPACE}:/django-home"
                }
            }
            steps {
                sh """
                    python --version
                    python /django-home/manage.py test
                """
            }
        }
        
        stage ('build'){
            steps{
                sh '''
                ver=`grep 'image:' k8s-deploy.yaml | cut -d ':' -f3`
                docker build -t k8s-repo.io/dms:$ver ./dms/
                docker push k8s-repo.io/dms:$ver
                '''
            }
        }
        
        stage ('deploy'){
            steps{
                sh '''
                kubectl apply -f k8s-deploy.yaml
                '''
            }
        }
    }
}