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

> **Info**: 
> These data are recommendations based on standards and observed averages on Sekoia.io, so they may change depending on use cases.

* Last version of Docker Engine. You will find all the installation process on the [official website](https://docs.docker.com/engine/install/)
* INBOUND TCP or UDP flows opened between the systems/applications and the concentrator on the ports of your choice
* OUTBOUND TCP flow opened towards:
  * **FRA1** intake.sekoia.io on port 10514 
  * **FRA2** fra2.app.sekoia.io on port 10514 
  * **MCO1** mco1.app.sekoia.io on port 10514 
  * **EUA1** app.uae1.sekoia.io on port 10514 
  * **USA1** app.usa1.sekoia.io on port 10514 
  

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

When debug is set to true, the raw event received and the output message will be printed in STDOUT. Each one will be respectively identified using tags: : [Input $INTAKE_KEY] & [Output $INTAKE_KEY]

### Docker-compose file
To ease the deployment, a `docker-compose.yml` file is suggested and a template is given.

#### Environment variables
This image uses two environment variables to customize the container. These variables are used to define a queue for incoming logs in case there is an temporaly issue in transmitting events to Sekoia.io. The queue stores messages in memory up to a certain number of events and then store them on disk.

```yaml
environment:
    - MEMORY_MESSAGES=2000000
    - DISK_SPACE=180g
    - REGION=FRA1
```
* `MEMORY_MESSAGES=2000000` means queues are allowed to store up to 2,000,000 messages in memory. If we consider a message size is 1.2KB, then you will use 2,4GB of RAM memory (2000000 * 1.2KB = 2.4GB). Note that this value is distributed among the configured intakes. For example, if 10 intakes are configured, each queue will have a retention capacity of 200,000 messages.
* `DISK_SPACE=180g` means that the total of all queues is allowed to store up to 180 gigabytes of messages on disk.
* `REGION=FRA1` is the region where to send the logs. Currently many options are available: `FRA1`, `FRA2`, `MCO1`, `USA1`, `UAE1` or `OTHER` combined with the `ENDPOINT` variable to define a custom destination

[Here](#prerequisites) you will find recommendations to set these variables based on the number of assets. You can also define your own values, which should be chosen according to your virtual machine's template.

> **Info**: 
>  In case you want to set a specific retention size in memory for a particular intake, you can define it using this type of configuration:
>  ```yaml
>  - name: Techno1
>    protocol: tcp
>    port: 20516
>    intake_key: INTAKE_KEY_FOR_TECHNO_1
>    queue_size: 100000
>  ```
>  Note that other intakes will retain their default values, which is MEMORY_MESSAGES divided by the total number of intakes.

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
    - ./disk_queue:/var/spool/rsyslog
```

* `./intakes.yaml:/intakes.yaml` is used to tell Rsyslog what ports and intake keys to use.
* `./disk_queue:/var/spool/rsyslog` is used when the rsyslog queue stores data on disk. The mapping avoids data loss if logs are stored on disk and the container is deleted.

#### Import a custom rsyslog configuration 

You can add your own additional rsyslog configuration. It can be useful to deal with specific use cases which are not supported natively by the Sekoia.io concentrator. To enable it, you simply have to create a new folder called `extended_conf` and put an additional your rsyslog file into (your file must have the extension *.conf). You do not have to deal with the `intake.yaml` file. Your custom configuration will be added in addition to the intake definition and will not erase exisiting ones. 

You can define your own method for obtaining logs using rsyslog modules, but you still need to forward events to Sekoia.io by providing a syslog-valid message with your intake key as a header, as follows:

```bash
input(type="imtcp" port="20521" ruleset="remote20521")
template(name="SEKOIAIO_Template" type="string" string="<%pri%>1 %timegenerated:::date-rfc3339% %hostname% MY-APP-NAME - LOG [SEKOIA@53288 intake_key=\"MY-INTAKE-KEY\"] %msg%\n")
ruleset(name="remote20521"){
action(
    name="action"
    type="omfwd"
    protocol="tcp"
    target="intake.sekoia.io"
    port="10514"
    TCP_Framing="octet-counted"
    StreamDriver="gtls"
    StreamDriverMode="1"
    StreamDriverAuthMode="x509/name"
    StreamDriverPermittedPeers="intake.sekoia.io"
    Template="SEKOIAIO_Template"
    )
}
```

Once additional configuration has been added, you simply have to mount them in the docker as following: 

```yaml
volumes:
    - ./intakes.yaml:/intakes.yaml
    - ./extended_conf:/extended_conf
    - ./disk_queue:/var/spool/rsyslog
```

#### Additional options

```yaml
restart: always
pull_policy: always
```

* `restart: always`: this line indicates to restart the concentrator everytime it stops. That means if it crashes, if you restart Docker or if you restart the host, the concentrator will start automatically.
* `pull_policy: always`: docker compose will always try to pull the image from the registry and check if a new version is available for the tag specified.

## Configure TLS for an Intake

Sending logs between the forwarder and Sekoia is always encrypted with TLS. However, by default, if you use the `tcp` or `udp` protocol option in your intake configuration, the logs between your devices and the forwarder will not be encrypted. This section shows you how to configure TLS between a source and the forwarder.

### Configuration of the docker-compose.yml

Activating TLS requires setting up an encryption key, a certificate, and a CA certificate. These should be placed in the `./certs` directory within the forwarder's directory.
Therefore it is necessary to mount this volume. Add the following line to the configuration:

```yaml
volumes:
    - ./certs:/certs
    [...]
```

### Creating the Key and Certificate

We will now create the key and certificate that will be used for encryption. In this case, we will create a self-signed certificate, meaning that the server certificate and the CA (Certificate Authority) certificate will be the same. If you have expertise in managing certificates, you can create a certificate signed by a real CA.

**Step one**: Create the directory and navigate to it:

```
mkdir certs && cd certs
```

**Step two**: Install OpenSSL

=== "Debian, Ubuntu"

    ```bash
    sudo apt update
    sudo apt install -y openssl
    ```

=== "Fedora, Red Hat, CentOS (yum)"

    ```bash
    sudo yum update
    sudo yum install -y openssl
    ```

=== "Fedora, Red Hat, CentOS (dnf)"
    
    ```bash
    sudo dnf update
    sudo dnf install -y openssl
    ```

Step three: Create the key and certificate

```
openssl req -x509 \
            -sha256 -days 1825 \
            -nodes \
            -newkey rsa:4096 \
            -keyout server.key -out server.crt
```

- `openssl req`: Launches the process to create a Certificate Signing Request (CSR) or a self-signed certificate.
- `-x509`: This option tells OpenSSL to generate a self-signed certificate rather than a CSR.
- `-sha256`: Specifies that the SHA-256 hashing algorithm should be used for the certificate's signature.
- `-days 1825`: Sets the certificate's validity period to 1825 days, which corresponds 5 years.
- `-nodes`: This stands for "no DES" and indicates that the private key should not be encrypted, meaning no password will be required to use the private key.
- `-newkey rsa:4096`: Generates a new RSA key pair of 4096 bits in length, and simultaneously creates a certificate request using this key pair.
- `-keyout server.key`: Specifies the file where the generated private key should be saved. In this case, it will be saved to `server.key`.
- `-out server.crt`: Specifies the file where the generated self-signed certificate should be saved. In this case, it will be saved to `server.crt`.

**Step four**: Change permissions on the files

```
chmod 600 server.key server.crt
```

## Usage
To start (and create if needed) the container:
```bash
sudo docker compose up -d
```

To start (and create if needed) the container in interactive mode:
```bash
sudo docker compose up
```

To view container logs when using the Debug variable:
```bash
sudo docker compose logs
```

To view container logs for a specific intake when using the Debug variable:
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