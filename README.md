# SEKOIA.IO Docker concentrator - BETA
**Important**: This project is currently in BETA

The files in this repository are used to build and create a Docker container running a Rsyslog as a concentrator to forward events to SEKOIA.IO.

To catch incoming events and apply the right intake key, this image processes each source on a specific TCP port.

The build is based on Ubuntu 22.04 and will install all the required components.

## Prerequisites
To be able to run the container you need :

* A x86-64 Linux host
* Last version of Docker Engine. You will find all the installation process on the [official website](https://docs.docker.com/engine/install/)
* INBOUND TCP flows between your systems/applications and this host on the ports of your choice
* OUTBOUND TCP flow to intake.sekoia.io on port 10514

## intakes.yaml file
The `intakes.yaml` file is used to tell Rsyslog what ports and intake keys to use.
In the `intakes` key, specify:
* a name (no spaces allowed, but it has nothing to do with SEKOIA.IO, it can be a random value)
* a port to process incoming events
* the intake key

**Example**:
```yaml
---
intakes:
- name: windows
  port: 20516
  intake_key: INTAKE_KEY_FOR_WINDOWS
- name: harfanglab
  port: 20517
  intake_key: INTAKE_KEY_FOR_HARFANGLAB
- name: fortigate
  port: 20518
  intake_key: INTAKE_KEY_FOR_FORTIGATE
```

## Docker-compose file
To ease the deployment, a `docker-compose.yml` file is suggested and a template is given.

### Logging

```yaml
    logging:
      options:
        max-size: "1000m"
        max-file: "2"
```
Docker logging system give you the flexibility to view events received on the container in real time with the command `docker logs <container_name>`. These logs are stored by default in `/var/lib/docker/containers/<container_uuid>/<container_uuid>-json.log`. To avoid the overload of disk space, some options are specified. `max-size` specifies the max size a one file and `max-file` specifies the total number of files allowed. When the maximum number of files is reached, a log rotation is performed and the oldest file is deleted.

### Environment variables
This image uses two environment variables to customize the container. These variables are used to define a queue for incoming logs in case there is an temporaly issue in transmitting events to SEKOIA.IO. The queue stores messages in memory up to a certain number of events and then store them on disk.

```yaml
    environment:
      - MEMORY_MESSAGES=100000
      - DISK_SPACE=32g
```
* `MEMORY_MESSAGES=1000000` means the queue is allowed to store up to 100000 messages in memory. Since in the image configuration, the maximum value of a message is 20k, 100000 means `100000 * 20000 = 2G`
* `DISK_SPACE=32g` means the queue is allowed to store on disk up to 32 giga of messages.

### Ports
Ports in Docker are used to perform port forwarding between the host running the container and the container itself.
```yaml
    ports:
      - "20516-20518:20516-20518"
```

`20516-20518:20516-20518` means that every packets coming through the TCP port `20516`, `20517` or `20518` to the host will be forwarded to the Rsyslog container on the port `20516`, `20517` or `20518`. Please adapt these values accordingly to the `integrations.csv` file.

### Volumes

Volumes are used to share files and folders between the host and the container.

```yaml
    volumes:
      - ./integrations.csv:/integrations.csv
      - ./conf:/etc/rsyslog.d
      - ./rsyslog:/var/spool/rsyslog
```

* `./integrations.csv:/integrations.csv` is used to tell Rsyslog what ports and intake keys to use.
* `./conf:/etc/rsyslog.d` is mapped if you want to customize some rsyslog configuration (ADVANCED)
* `./rsyslog:/var/spool/rsyslog` is used when the rsyslog queue stores data on disk. The mapping avoids data loss if logs are stored on disk and the container is deleted.

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

To stop the container:
```bash
sudo docker compose stop
```

To delete the container (container needs to be stopped):
```bash
sudo docker compose rm
```

## OPTIONAL: Build the image
If you don't want to use the image available at `ghcr.io/sekoia-io/sekoiaio-docker-concentrator:latest` - **NOT RECOMMENDED** -, you can also build the image on your own.

To build the image:
```bash
docker build . -t sekoiaio-docker-concentrator:latest
```

**Note**: Be sure to adapt the `docker-compose.yml` accordingly and change `image: ghcr.io/sekoia-io/sekoiaio-docker-concentrator:latest` by `image: sekoiaio-docker-concentrator:latest` if you use this method.