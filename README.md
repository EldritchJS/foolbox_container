## Containerized Foolbox adversarial image generation

Intended for deployment on an OpenShift cluster. Expects an available Kafka broker, which can be created with the following commands:

1. `oc create -f https://raw.githubusercontent.com/strimzi/strimzi-kafka-operator/0.1.0/kafka-inmemory/resources/openshift-template.yaml`
2. `oc new-app strimzi`

The adversarial generator also expects a repo containing a Foolbox Model Zoo compatible model. An example repo/model used by default is the CIFAR10 challenge model provided by Foolbox and forked [here](https://github.com/EldritchJS/cifar10_challenge)

The generator expects a JSON object with keys `url` and `label` for the url of the image to be attacked and its true label, respectively. It will attempt to generate an adversary image and report the model's prediction for the original image and its adversary.

An example JSON object generator which publishes to a Kafka topic this generator consumes can be found [here](https://github.com/EldritchJS/url_label_producer) which can be created in an OpenShift pod as follows:

`oc new-app centos/python36-centos7~https://github.com/eldritchjs/url_label_producer`


The adversarial image generator pod is created as follows:

`oc new-app centos/python36-centos7~https://github.com/eldritchjs/foolbox_container`
