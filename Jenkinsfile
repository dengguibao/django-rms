pipeline {
    agent any
    options { 
        disableConcurrentBuilds() 
    }
    stages {
        stage ('pull code') {
            steps{
                checkout scm
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
                docker build -t k8s-repo.io/dms:$ver .
                docker push k8s-repo.io/dms:$ver
                '''
            }
        }
        
        stage ('deploy'){
            steps{
                sh '''
                ls -l
                export KUBECONFIG=/etc/kubernetes/admin.conf
                kubectl get pods
                kubectl apply -f k8s-deploy.yaml
                '''
            }
        }
    }
}