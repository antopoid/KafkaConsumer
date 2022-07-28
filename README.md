# Kafka Python Consumer (Windows)

**This is a kafka consumer python programm, wich deserialize data from an avro schema registry and access is managed by kerberos and security by ssl** 

**It aim to be as simple as possible, clone it, configure it, launch it and get records instantly**

Authors: Antoine Poidevin @apoidev & Nils Faure @nfaure in the team @SSDD
Using: [confluent-kafka-python](https://github.com/confluentinc/confluent-kafka-python), [DhiaTN](https://github.com/DhiaTN/confluent-avro-py), [Apache kafka](https://github.com/apache/kafka)
<details>
<summary>Summary</summary>

[[_TOC_]]

</details>


<details>
<summary>Requirements</summary>

*For it to work, you need these Files and Access requirement:*
- krb5.ini (for windows), or krb5.conf (for linux)
- SSL certificate
- a Keytab file used for Kafka broker authentication
- a kafka broker to access
- a kafka topic
- a group id
- schemaregistry adress to access
- password and username for the schema registry
 
***Conda requirement***

- krb5
- Pyhton verison:3.7

***Python requirement***

*Libraries listed below:*
- [x] certifi==2022.5.18.1
- [x] charset-normalizer==2.0.12
- [x] confluent_avro==1.8.0
- [x] decorator==5.1.1
- [x] fastavro
- [x] gssapi==1.7.3
- [x] idna==3.3
- [x] kafka-python==2.0.2
- [x] python-status==1.0.1
- [x] requests
- [x] urllib3==1.26.9
- [x] wincertstore==0.2
</details>

## Tutorials (Optional step not mandatory)
We wrote basic kafka tutorials that use docker and your local environnment in order to make you understand the basic kafka aspects.
1. You can start by reading the doc in `./Tutorial_kafka/Tutorial local access/Tutorial_kafkabasics/Introduction.docx` 
2. And after that you can follow the tutorial from 0 to 3.
3. Have fun an good luck !
4. A file explanation is also available in `./Tutorial_kafka/File_explanation`

## User Manual

### 1. Installing and Configuring your env
*(All the steps below needs to be done on the bastion or server, your own local computer will be used just to download files)*

*(Use the share drive to transfer files from you local computer to the bastion)*
1. Clone the repository in your computer: `git clone https://github.com/antopoid/KafkaConsumer.git`
2. You can also download all the software needed from [here](https://cloud.antopoid.com/s/7apLtjcrRXfZMZT)
3. Download miniconda, Install it (click next with default values) you can use another python env manager but this one make a lot of steps easier: [Download here](https://conda.io/miniconda.html)
4. You can download and use my environment: [here](https://cloud.antopoid.com/s/ymg3qxGbT99AEae)
5. Now unzip and put your env in `C:\Users\username\Miniconda3\envs` and activate it by typing in miniconda:  `conda activate kafka`
6. Launch miniconda and create your first env (or if you downloaded mine skip this step): `conda env create -f environment.yml`
7. Move into the folder where you cloned the git repository `cd /your/path/to/git/repo`
8. Enter in your env by activating it: `conda activate kafka`
9. Check if python is properly installed, type in miniconda: `python --version` (if python is not installed type in `conda install python==3.7`)
10. Install all the python modules that kafka need: `pip install -r requirements.txt`
11. Move the file krb5.ini in: `C\Windows\krb5.ini` (the only step where you might need admin rights, mandatory to put it here)
12. Use sublime text to edit your files
*Remember that on the bastion YOU DO NOT HAVE ACCESS TO INTERNET*

### 2. Preparing the kafka consumer
1. Open the file configuration.ini in a text editor and change the values with yours folowing that:
```
[KafkaConsumer]
topic:                      Name of the topic taht you want to access, for instance FOO.BAR.TEST.1
groupid:                    Name of the groupid that have access to the given topic, for instance foobar-test
bootstrap:                  Address of the kafka broker, for instance kafkabrokerfoobar.aws.com or 10.55.156.39 (default port is 9092)
offset: earliest            Placement of the consumer concerning the offset, 'earliet' mean the first records 'latest' mean the last records (ONLY latest or earliest nothing else)


[SchemaRegistry]
address:                    Adress of the schema registry, for instance schemaregistryfoobar.aws.com or 10.55.156.39 (default port is 80)
username:                   Username needed to authenticate if basic http auth is enable
password:                   Password needed to authenticate if basic http auth is enable  

[Security]
sslcafile:                  Path for the ssl certificate file, for instance C:\kafka\ssl.cert
saslmechanism:              Leave this one on GSSAPI (execpt if you know what you are doing)
securityprotocol:           Leave this one on SASL_SSL (execpt if you know what you are doing)
servicename:                DO NOT CHANGE THIS ONE (only kafka)
keytab:                     Path for the keytab file needed for kerberos, for instance C:\kafka\kerberos.keytab
principalname:              Name used for the kerberos authentication, for instance foobartest@FOO.BAR.TEST
```

### 3. Checking the network
1. Ping the kafka broker in order to check if the connection is valid: `ping kafkabrokerfoobar.aws.com`
2. Check if the port for the kafka broker is available and can be accessed: `telnet kafkabrokerfoobar.aws.com 9092`
3. Do exactly the same steps for the schema registry and the kerberos service
4. Ask to your Network admin to setup firewall rules between your computer and the different services if needed (kafka broker, schema registry, kerberos)

### 4. Testing kafka records (Optional step not mandatory)
1. Download official kafka binary of apache: [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.2.0/kafka-3.2.0-src.tgz)
2. Place it under the directory: `C:\kafka`
3. Download and install Java development kit (if you dont have admin rights do the next steps on another computer): [here](https://www.oracle.com/java/technologies/javase-jdk15-downloads.html)
4. In miniconda type this: `keytool -export -alias mydomain -file mysslcert.crt -keystore mykeystore.jks`
5. Open the file `consumer.properties` with a text editor and changes the values with yours (group.id, ssl.truststore.location, ssl.truststore.password, keyTab, principal)
6. Now in miniconda launch the kafka console consumer by typing this and changing with your values: `C:\kafka\kafka-console-consumer.bat --bootstrap-server 10.55.156.39:9092 --topic FOO.BAR.TEST.1 --consumer.config C:\path\to\your\consumer.properties`
7. If everything is working as expected you should see values in Hexadecimal like this (if avro serializer is enable): /0x89/0x29/0xAE/...
8. You can enable the kafka debugger by going into `C:\Kafka\config\tools-log4j.properties` and changing the line from `log4j.rootLogger=warn, stderr` to `log4j.rootLogger=debug, stderr`

### 5. Using it as the main file
1. First of all get in touch with the script by doing: `python Compiled_Kafka_Consumer_library.py -h`
2. You should get an error like: `No Brokers available` 
3. So Now lets get a valid ticket from the kerberos service: `python Compiled_Kafka_Consumer_library.py -k`
4. To stop the kafka consumer you should use the <kbd>Ctrl</kbd><kbd>C</kbd>or <kbd>Ctrl</kbd><kbd>Z</kbd> command binds.
5. Usualy the ticket is valid for 24h, so remember to launch it at least once a day to get a new valid ticket back.
6. Get the help description by going again: `python Compiled_Kafka_Consumer_library.py -h`
7. You can now list all the topic that you have access with your group id: `python Compiled_Kafka_Consumer_library.py -t`
8. The results of the argument `-t` is stored in the file `./topics.json`
9. To start getting records instantly, just use the command: `python Compiled_Kafka_Consumer_library.py`
10. The records are printed in the folder: `./records/TOPICNAME.json`
11. Each line in the `./records/TOPICNAME.json` is written as a json object independant from the next line.
12. if you want to read the data within python for the file`./records/TOPICNAME.json` where the lines looks like this:
`{"key": {"logical_input_port": 26, "elementary_band": 837, "channel_name": "UNKNOWN_CHANNEL_NAME"}, "value": {"spectrum": {"logical_input_port": 26, "elementary_band": 837, "measurement": -58.23440170288086, "timestamp": 1657013813725141760}}}`
You should use: 
```python
for line in open('./records/TOPICNAME.json', 'r'):
    listvalues["line " + str(i)] = json.loads(line)
for line in listvalues:
    channel_name = listvalues["line " + str(i)]['value']['channel_measurement']['channel_name']
    i = i + 1
i = 0
```
13. After using at least one time the `-t` argument, you can now use the `-cu` argument to check if there are any updates on the availbale topics.

### 6. Using it as a library
*Start by reading the second part of the `Compiled_Kafka_Consumer_library.py` script, which contains modules which are not used when running the library as a main file. What you can do now is to import the modules you need for your kafka consumer; there are 2 scenarios possible:*

First, you can choose to only import the kerberos authentification and pre-made kafka consumer;
1. Import `basic_kafka_consumer_schema_stream` and `initialising_kerberos_ticket` in your python file for the consumer
2. Set the `key_path` (string), `principal_name` (string), and the `length_kerberos_ticket` (integer) variables for the `initialising_kerberos_ticket` function to match your given credentials
3. Set these shown parameters for the kerberos consumer (`basic_kafka_consumer`); these parameters will set the key aspects of the kafka consumer 
    a. `shema_registry_link` (string) -> link to the schema registry |
    b. `Username` (string) -> schema registry username |
    c. `Password` (string) -> schema registry password |
    d. `Topic` (string) -> topic name to access in kafka broker |
    e. `bootstrap_server` (string) -> bootstrap server for the kafka broker |
    f. `GroupID` (string) -> groupid for kafka broker to know who accesses |
    g. `auto_commit` (string) -> to tell the broker last time you read |
    h. `when_to_get_data` (string) -> latest or earliest record |
    i. `certificat_path` (string) -> path to SSL certificat |
4. To `basic_kafka_consumer` there are also optional parameters that can be set, where the default settings are chosen if the parameter is not specified:
    a. `pre_time_out_func_variables` (list) -> list of variables for the function running befor ethe we read data from the broker (default = `''`) |
    b. `pre_time_out_func` -> function which is performed before we start reading the kafka broker (default is a return of `[]`) |
    c. `func` -> function to analyse and manipulate per data extracted from kafka (default is a function with a list input and appends the message to the list) |
    d. `after_time_out_func`-> function intended to be use to save the messages read, but can be used for anything (defaul is a saving to text the elements of a list) |
    e. `consumer_timeout` (int) -> timeout of consumer time after last message is read(default is `100000`) |
    f. `security_proto` (string) -> security protocol (default is `SASL_SSL`) |
    g. `sasl_mechan` (string) -> sasl mechanism (default is `GSSAPI`) |
    h. `ssl_check_host` (string) --> ssl check  (default is `false`) |
    i. `file_name` (string) -> file name where to save data (default is`kafka_stream_output.txt`)

Second you can choose to build your own consumer by seperating these stages:
1. Reading the deserialiser from the schema registry with the `schema_registry_deserialiser` function
2. Configuring the kafka consumer with the `initialising_kafka_consumer` function
3. Reading the values in the kafka broker and deserialising with `get_kafka_stream`

With this set up you fill in the same variables for the already made consumer function which you can learn how to set up above, but you have more freedom
in the overall architecture of your code. It can also be easier to debu if you use the seperate functions.



## Debugging
**You can enable the kafka debugger by passing the -d argument `python Compiled_Kafka_Consumer_library.py -d`**
### ' No Brokers available '
- Most of the time this erros shows up when you dont have a valid kerberos ticket, so try to clean your tickets `klist purge` and get a new one with `python Compiled_Kafka_Consumer_library.py -k`
- It can also show up when the kafka broker is overloaded, so wait a bit and try again.
- It can also happend if you did a mistake in your kafka broker address or port
- This can also happen if you do not have access through the firewall

### No records poping up in the cli 
- The given topic dont have any records
- The end offset = beginning offset, this means that all the records are expired 
- the associated schema for the topic is not well written or you dont have access to it 

### Reading again the same records
- In the definition part for the kafka consumer, you can choose to disable autocommit (enable_auto_commit=False), this means that the kafka broker will not know if you have already seen or not the records, you can change it here:
```python
def kafkaconsumer():
    """
    # Goal: configuring the kafka consumer with kerberos and ssl cert
    # Input: Nothing
    # Output: class 'kafka.consumer.group.KafkaConsumer'
    """
    consumer = KafkaConsumer(KAFKA_TOPIC,
                             bootstrap_servers=BOOTSTRAP_SERVER,
                             group_id=GROUP_ID,
                             enable_auto_commit=True,  # if set to true means you can receive the records only once
                             auto_offset_reset=AUTO_OFFSET_RESET,
                             ssl_check_hostname=False,
                             ssl_cafile=SSL_CAFILE,
                             security_protocol=SECURITY_PROTOCOL,
                             sasl_mechanism=SASL_MECHANISM,
                             sasl_kerberos_service_name=SALS_KERBEROS_SERVICE_NAME,
                             consumer_timeout_ms=15000, )
    return consumer
```
- If enable_auto_commit was allready set to true for the groupid that you are using, you should change it from `testdev-apoidev` to `testdev-apoidev1` for instance, in order to completely reset the consumer.

You can run the consumer by importing the kafka consumer python script into
your code, inputing the required fields in the function.
