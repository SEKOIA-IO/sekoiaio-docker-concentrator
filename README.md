# Sekoia.io Forwarder

The files in this repository are used to build and create a Docker container running a Rsyslog as a concentrator to forward events to Sekoia.io.

To catch incoming events and apply the right intake key, this image processes each source on a specific TCP port.

The build is based on Ubuntu 22.04 and will install all the required components.

## Prerequisites
To be able to run the container you need:

* A x86-64 Linux host using one of these templates:
  | Number of assets |  vCPUs |  RAM (Go) | Disk size (Go) | Sekoia concentrator settings                |
  |------------------|:------:|:---------:|:--------------:|:-------------------------------------------:|
  | 1000             |    2   |   4       |      200       |  MEMORY_MESSAGES=2000000 / DISK_SPACE=180g  |
  | 10 000           |    4   |   8       |      1000      |  MEMORY_MESSAGES=5000000 / DISK_SPACE=980g  |
  | 50 000           |    6   |   16      |      5000      |  MEMORY_MESSAGES=12000000 / DISK_SPACE=4980g |

  !!! info 
      These data are recommendations based on standards and observed averages on Sekoia.io, so they may change depending on use cases.

* Last version of Docker Engine. You will find all the installation process on the [official website](https://docs.docker.com/engine/install/)
* INBOUND TCP or UDP flows opened between the systems/applications and the concentrator on the ports of your choice
* OUTBOUND TCP flow opened towards intake.sekoia.io on port 10514

## Docker-compose folder
The docker-compose folder contains the two files needed to start the container with docker compose: `docker-compose.yml` and `intakes.yaml`

### intakes.yaml file
The `intakes.yaml` file is used to tell Rsyslog what ports and intake keys to use.
In the `intakes` key, specify:
* a name (it has nothing to do with Sekoia.io, it can be a random value)
* the protocol, tcp or udp
* a port, to process incoming events
* the intake key

**Example**:
```yaml
---
intakes:
- name: Techno1
  protocol: tcp
  port: 20516
  intake_key: INTAKE_KEY_FOR_TECHNO_1
- name: Techno2
  protocol: tcp
  port: 20517
  intake_key: INTAKE_KEY_FOR_TECHNO_2
- name: Techno3
  protocol: tcp
  port: 20518
  intake_key: INTAKE_KEY_FOR_TECHNO_3
```

#### Debug 
A debug variable is available in order to debug a specific intake, for example 
```yaml
---
intakes:
- name: Techno1
  protocol: tcp
  port: 20516
  intake_key: INTAKE_KEY_FOR_TECHNO_1
- name: Techno2
  protocol: tcp
  port: 20517
  intake_key: INTAKE_KEY_FOR_TECHNO_2
  debug: True
- name: Techno3
  protocol: tcp
  port: 20518
  intake_key: INTAKE_KEY_FOR_TECHNO_3
```

By using this key, the raw received message and the output message will be printed in the console. Each one will be respectively identified using tags: : [Input $INTAKE_KEY] & [Output $INTAKE_KEY]

### Docker-compose file
To ease the deployment, a `docker-compose.yml` file is suggested and a template is given.

#### Logging

```yaml
logging:
    options:
    max-size: "1000m"
    max-file: "2"
```
Docker logging system enables you to view events received on the container in real time with the command `docker logs <container_name>`. These logs are stored by default in `/var/lib/docker/containers/<container_uuid>/<container_uuid>-json.log`. To avoid the overload of disk space, some options are specified. `max-size` specifies the max size a one file and `max-file` specifies the total number of files allowed. When the maximum number of files is reached, a log rotation is performed and the oldest file is deleted.

#### Environment variables
This image uses two environment variables to customize the container. These variables are used to define a queue for incoming logs in case there is an temporaly issue in transmitting events to Sekoia.io. The queue stores messages in memory up to a certain number of events and then store them on disk.

```yaml
environment:
    - MEMORY_MESSAGES=100000
    - DISK_SPACE=32g
```
* `MEMORY_MESSAGES=100000` means the queue is allowed to store up to 100,000 messages in memory. For instance, if your message size is 20KB, then you will use 2GB of RAM memory (100,000 * 20KB = 2GB).
* `DISK_SPACE=32g` means the queue is allowed to store on disk up to 32 giga of messages.

[Here](#prerequisites) you will find recommendations to set these variables based on the number of assets. You can also define your own values, which should be chosen according to your virtual machine's template.

#### Ports
Ports in Docker are used to perform port forwarding between the host running the container and the container itself.
```yaml
ports:
    - "20516-20518:20516-20518"
```

`20516-20518:20516-20518` means that every packets coming through the TCP port `20516`, `20517` or `20518` to the host will be forwarded to the Rsyslog container on the port `20516`, `20517` or `20518`. Please adapt these values according to the `intakes.yaml` file.

#### Volumes

Volumes are used to share files and folders between the host and the container.

```yaml
volumes:
    - ./intakes.yaml:/intakes.yaml
    - ./conf:/etc/rsyslog.d
    - ./disk_queue:/var/spool/rsyslog
```

* `./intakes.yaml:/intakes.yaml` is used to tell Rsyslog what ports and intake keys to use.
* `./conf:/etc/rsyslog.d` is mapped if you want to customize some rsyslog configuration (ADVANCED)
* `./disk_queue:/var/spool/rsyslog` is used when the rsyslog queue stores data on disk. The mapping avoids data loss if logs are stored on disk and the container is deleted.

#### Additional options

```yaml
restart: always
pull_policy: always
```

* `restart: always`: this line indicates to restart the concentrator everytime it stops. That means if it crashes, if you restart Docker or if you restart the host, the concentrator will start automatically.
* `pull_policy: always`: docker compose will always try to pull the image from the registry and check if a new version is available for the tag specified.

## Usage
To start (and create if needed) the container:
```bash
sudo docker compose up -d
```

To start (and create if needed) the container in interactive mode:
```bash
sudo docker compose up
```

To view container logs:
```bash
sudo docker compose logs
```

To view container logs for a specific intake:
```bash
sudo docker compose logs | grep "YOUR_INTAKE_KEY"
```

To stop the container:
```bash
sudo docker compose stop
```

To delete the container (container needs to be stopped):
```bash
sudo docker compose rm
```

## OPTIONAL: Build the image
If you don't want to use the image available at `ghcr.io/sekoia-io/sekoiaio-docker-concentrator` - **EXPERT MODE** -, you can also build the image on your own.

To build the image:
```bash
docker build . -t sekoiaio-docker-concentrator:latest
```

**Note**: Be sure to adapt the `docker-compose.yml` accordingly and change `image: ghcr.io/sekoia-io/sekoiaio-docker-concentrator:x` by `image: sekoiaio-docker-concentrator:latest` if you use this method.