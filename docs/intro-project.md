Now that you have an Upbound account and the up CLI installed, you're ready to create a control plane.

In this quickstart, you will:

Scaffold a control plane project
Define your own resource abstraction and templatization
See the changes immediately
TIP

This quickstart teaches how to use Crossplane to build workflows for templating resources and exposing them as simplified resource abstraction. If you just want to manage the lifecycle of resources in an external system through Crossplane and Kubernetes, read Manage external resources with providers

# Prerequisites​

This quickstart takes around 10 minutes to complete. You should be familiar with YAML or programming in Go, Python, or KCL.

Before beginning, make sure you have:

The up CLI installed
A Docker-compatible container runtime installed and running on your system
TIP

Podman users If you're using Podman instead of Docker, set the DOCKER_HOST environment variable to the Podman socket before running up commands:

```shell
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
```

# Create a control plane project​

Crossplane works by letting you define new resource types in Kubernetes that invoke function pipelines to template and generate other resources. Just like any other software project, a control plane project is a source-level representation of your control plane.

Create a control plane project on your machine by running the following command:

```shell
up project init --scratch getting-started
```


This scaffolds a new project in a folder called getting-started. Change your current working directory to the project root folder:

```shell
cd getting-started
```

# Deploy your control plane​

In the root directory of your project, build and run your project by running the following:

```shell
up project run --local --ingress
```


This launches an instance of Upbound Crossplane on your machine, wrapped and deployed in a container. Upbound Crossplane comes bundled with a Web UI.

# Define your own resource type​

Customize your control plane by defining your own resource type.

Create an example instance of your custom resource type with:

```shell
up example generate \
    --api-group platform.example.com \
    --api-version v1alpha1 \
    --kind WebApp\
    --name my-app \
    --scope namespace \
    --namespace default
```


Open the project in your IDE of choice and replace the contents of the generated file getting-started/examples/webapp/my-app.yaml with the following:

getting-started/examples/webapp/my-app.yaml
```yaml
apiVersion: platform.example.com/v1alpha1
kind: WebApp
metadata:
  name: my-app
  namespace: default
spec:
  parameters:
    image: nginx
    port: 8080
    replicas: 1
    service:
      enabled: true
    ingress:
      enabled: false
    serviceAccount: default
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "1"
status:
    availableReplicas: 1
    url: "http://localhost:8080"
```


Next, generate the definition files needed by Crossplane with the following commands in one of the languages:

- Go Templates
- Python
- Go
- KCL

```shell
up xrd generate examples/webapp/my-app.yaml
up composition generate apis/webapps/definition.yaml
up function generate --language=go-templating compose-resources apis/webapps/composition.yaml
up dependency add --api k8s:v1.33.0
```


You just created your own resource type called WebApp. You generated a function containing the logic Crossplane uses to determine what should happen when you create the WebApp.

TIP

To define a new resource type with Crossplane, you need to:

create a CompositeResourceDefinition (XRD), which defines the API schema of your resource type
create a Composition, which defines the implementation of that API schema.

A Composition is a pipeline of functions, which contain the user-defined logic of your composition.

Open the function definition file at getting-started/functions/compose-resources/ and replace the contents with the following:

- Go Templates
- Python
- Go
- KCL

getting-started/functions/compose-resources/01-compose.yaml.gotmpl
```yaml
# code: language=yaml
# yaml-language-server: $schema=../../.up/json/models/index.schema.json

---
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    gotemplating.fn.crossplane.io/composition-resource-name: deployment
    {{ if eq (.observed.resources.deployment | getResourceCondition "Available").Status "True" }}
    gotemplating.fn.crossplane.io/ready: "True"
    {{ end }}
  name: {{ .observed.composite.resource.metadata.name }}
  namespace: {{ .observed.composite.resource.metadata.namespace }}
  labels:
    app.kubernetes.io/name: {{ .observed.composite.resource.metadata.name }}
spec:
  replicas: {{ .observed.composite.resource.spec.parameters.replicas }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .observed.composite.resource.metadata.name }}
      app: {{ .observed.composite.resource.metadata.name }}
  strategy: {}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .observed.composite.resource.metadata.name }}
        app: {{ .observed.composite.resource.metadata.name }}
    spec:
      serviceAccountName: {{ .observed.composite.resource.spec.parameters.serviceAccount }}
      containers:
      - name: {{ .observed.composite.resource.metadata.name }}
        image: {{ .observed.composite.resource.spec.parameters.image }}
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: {{ .observed.composite.resource.spec.parameters.port }}
          protocol: TCP
        resources:
          requests:
            memory: {{ .observed.composite.resource.spec.parameters.resources.requests.memory }}
            cpu: {{ .observed.composite.resource.spec.parameters.resources.requests.cpu }}
          limits:
            memory: {{ .observed.composite.resource.spec.parameters.resources.limits.memory }}
            cpu: {{ .observed.composite.resource.spec.parameters.resources.limits.cpu }}
      restartPolicy: Always
status: {}

{{ if .observed.composite.resource.spec.parameters.ingress.enabled }}
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    gotemplating.fn.crossplane.io/composition-resource-name: ingress
    {{ if (get (getComposedResource . "ingress").status.loadBalancer.ingress 0).hostname }}
    gotemplating.fn.crossplane.io/ready: "True"
    {{ end }}
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
    alb.ingress.kubernetes.io/target-group-attributes: stickiness.enabled=true,stickiness.lb_cookie.duration_seconds=60
  name: {{ .observed.composite.resource.metadata.name }}
  namespace: {{ .observed.composite.resource.metadata.namespace }}
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {{ .observed.composite.resource.metadata.name }}
            port:
              number: 80
{{ end }}

{{ if .observed.composite.resource.spec.parameters.service.enabled }}
---
apiVersion: v1
kind: Service
metadata:
  annotations:
    gotemplating.fn.crossplane.io/composition-resource-name: service
    {{ if (get (getComposedResource . "service").spec "clusterIP") }}
    gotemplating.fn.crossplane.io/ready: "True"
    {{ end }}
  name: {{ .observed.composite.resource.metadata.name }}
  namespace: {{ .observed.composite.resource.metadata.namespace }}
spec:
  selector:
    app: {{ .observed.composite.resource.metadata.name }}
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: http
status:
  loadBalancer: {}
{{ end }}

---
apiVersion: {{ .observed.composite.resource.apiVersion }}
kind: {{ .observed.composite.resource.kind }}
status:
  {{ with $deployment := getComposedResource . "deployment" }}
  availableReplicas: {{ $deployment.status.availableReplicas | default 0 }}
  {{ else }}
  availableReplicas: 0
  {{ end }}
  {{ with $ingress := getComposedResource . "ingress" }}
  {{ with $hostname := (get $ingress.status.loadBalancer.ingress 0).hostname }}
  url: {{ $hostname | quote }}
  {{ else }}
  url: ""
  {{ end }}
  {{ else }}
  url: ""
  {{ end }}
```


Deploy the changes you made to your control plane:

```shell
up project run --local --ingress
```

TIP

The project run command builds and deploys any changes. If you don't have a control plane running yet, it creates one, otherwise it targets your existing control plane.

# Use the custom resource​

Your control plane now understands WebApp resources. Create a WebApp:

```shell
kubectl apply -f examples/webapp/my-app.yaml
```


Check that the WebApp is ready:

```shell
kubectl get -f examples/webapp/my-app.yaml
NAME     SYNCED   READY   COMPOSITION   AGE
my-app   True     True    app-yaml      56s
```


Observe the Deployment and Service Crossplane created when you created the WebApp:

```shell
kubectl get deploy,service -l crossplane.io/composite=my-app
NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-app-2r2rk   2/2     2            2           11m
```

```shell
NAME                   TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/my-app-xfkzg   ClusterIP   10.96.148.56   <none>        8080/TCP   11m
```

# Next steps​

Now that you know the basics of building with Upbound, create an AI-augmented operation to detect and remediate Kubernetes app workload errors. Read Create an AI-augmented operation.
