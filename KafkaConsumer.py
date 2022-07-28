#"This is the compiled Kafka consumer library, made from both the branches of the authors: Antoine Poidevin and Nils Faure."

#######################################
######## MAIN CODE FOR PROD ENV #######
#######################################
# Libraries
import datetime
import sys, os
import time  # Used for delays
import configparser  # Used for configfile.ini
import argparse  # Libraries for passing arguments when launching pyhton code
import json  # Used to treat json objects and files
import subprocess  # Used to exec windows cmd
from kafka import KafkaConsumer, TopicPartition
from confluent_avro import AvroKeyValueSerde, SchemaRegistry
from confluent_avro.schema_registry import HTTPBasicAuth

# Checking if the config file exist and if so reading it
Config = configparser.ConfigParser()
if not os.path.isfile("configuration.ini"): 
    quit("Configuration file needed ! No configuration.ini files found in the current directory !")
Config.read("configuration.ini")

# All global useful variables
KAFKA_TOPIC = Config.get('KafkaConsumer', 'topic')
GROUP_ID = Config.get('KafkaConsumer', 'groupid')
BOOTSTRAP_SERVER = Config.get('KafkaConsumer', 'bootstrap')
AUTO_OFFSET_RESET = Config.get('KafkaConsumer', 'offset')
SSL_CAFILE = Config.get('Security', 'sslcafile')
SECURITY_PROTOCOL = Config.get('Security', 'securityprotocol')
SASL_MECHANISM = Config.get('Security', 'saslmechanism')
SALS_KERBEROS_SERVICE_NAME = Config.get('Security', 'servicename')
SCHEMA_ADDRESS = Config.get('SchemaRegistry', 'address')
SCHEMA_USERNAME = Config.get('SchemaRegistry', 'username')
SCHEMA_PASSWORD = Config.get('SchemaRegistry', 'password')
KEYTAB = Config.get('Security', 'keytab')
PINCIPAL_NAME = Config.get('Security', 'principalname')


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


def schemaregistry():
    """
    # Goal: configuring the schema registry access
    # Input: Nothing
    # Output: class 'confluent_avro.schema_registry.client_http.SchemaRegistry'
    """
    registry_client = SchemaRegistry(
        SCHEMA_ADDRESS,
        HTTPBasicAuth(SCHEMA_USERNAME, SCHEMA_PASSWORD),
        headers={"Content-Type": "application/vnd.schemaregistry+json"}, )
    return registry_client


def avroserde(registry_client:object, KAFKA_TOPIC:str):
    """
    # Goal: configuring the avro deserializer
    # Input: registry_client = class 'confluent_avro.schema_registry.client_http.SchemaRegistry'
    #        KAFKA_TOPIC =  string (topic name)
    # Output: class 'confluent_avro.schema_registry.client_http.SchemaRegistry'
    """
    avroSerde = AvroKeyValueSerde(registry_client, KAFKA_TOPIC)
    return avroSerde


def runwincmd(cmd:str):
    """
    # Goal: execute command in the command prompt as a new process and return the code (windows)
    # Input: string (command to exec)
    # Output: Nothing
    """
    result = []
    process = subprocess.Popen(cmd,
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    for line in process.stdout:
        result.append(line)
    errcode = process.returncode
    for line in result:
        print(line)
    if errcode is not None:
        raise Exception('cmd %s failed, see above for details', cmd)


def getpartition(topic:str):
    """
    # Goal: Get the number of the partiton assigned for a given topic
    # Input: string (topic name)
    # Output: int
    """
    partition = consumer.partitions_for_topic(topic).pop()
    return partition


def getoffsets(topic:str, string:str):
    """
    # Goal: Get the end or beginning offset for a given topic
    # Input: topic = string (topic name)
    #        string = string ( 'beginning' or 'end' )
    # Output: int
    """
    PARTITIONS = []
    for partition in consumer.partitions_for_topic(topic):
        PARTITIONS.append(TopicPartition(topic, partition))
    if string == 'beginning':
        beginning_offsets = consumer.beginning_offsets(PARTITIONS)
        for k, v in beginning_offsets.items():
            return v
    if string == 'end':
        end_offsets = consumer.end_offsets(PARTITIONS)
        for k, v in end_offsets.items():
            return v


def preparefile(filename:str):
    """
    # Goal: Check and create directory to host records, check and create files for records as well
    # Input: string (path and name of the file)
    # Output: Nothing
    """
    if not os.path.isdir("./records"):
        os.mkdir("./records")
    with open(filename, "w") as outfile:
        outfile.write('')
        outfile.close()


def writejson(dic:dict, filename:str):
    """
    # Goal: Write into the given file the given dictionnary as JSON
    # Input: dic = dictionnary
    #        filename = (path and name of the file)
    # Output: Nothing
    """
    json_object = json.dumps(dic)  # ,indent = 4
    with open(filename, "a") as outfile:
        outfile.write(json_object)
        outfile.write("\n")


def listtopics(string:str):
    """
    # Goal: List all the topics available for a given group and write the results in ./topics.json file and print them in the command prompt (show or hide)
    # Input: string ('show' or 'hide' the results)
    # Output: Nothing
    """
    from prettytable import PrettyTable
    t = PrettyTable(['Topic', 'Beginning offset', 'End offset'])
    listtopics = set(consumer.topics())
    if string == "show": print(" List of topics for ", GROUP_ID, "\n", "Processing, please wait")
    filename = "./topics.json"
    preparefile(filename)
    for topics in listtopics:
        beginning = getoffsets(topics, 'beginning')
        end = getoffsets(topics, 'end')
        t.add_row([topics, beginning, end])
        dic = {"topic": {'name': topics, "beginning": beginning, "end": end}}
        writejson(dic, filename)
    if string == "show": print(t)
    print("This list has been written in the file ./topics.json")


def arguments():
    """
    # Goal: Initiliaze, configure and execute arguments and their effects (can be showed with '-h' argument)
    # Input: Nothing
    # Output: Nothing
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
        ----------------------------------------------------------
        Kafka consumer with Kerberos auth and AVRO Schema-Registry
        ----------------------------------------------------------
        
        ''')
    parser.add_argument('-d', help=" --- Enable debugging", dest="wants_debug",
                        action='store_true', required=False, default=False)
    parser.add_argument('-t', help=" --- Get all topics the user is authorized to view", dest="wants_list_topics",
                        action='store_true', required=False, default=False)
    parser.add_argument('-p', help=" --- Get the Partitions currently assigned to this consumer",
                        dest="wants_partitions",
                        action='store_true', required=False, default=False)
    parser.add_argument('-so', help=" --- Seek to the oldest and newest available offset for partitions.",
                        dest="seek_to_beginning",
                        action='store_true', required=False, default=False)
    parser.add_argument('-k', help=" --- Execute kinit process to get kerberos authentication ticket",
                        dest="kerberos_ticket",
                        action='store_true', required=False, default=False)
    parser.add_argument('-cu', help=" --- Check for updates on every topics based on the ./topics.json file",
                        dest="check_topics_upates",
                        action='store_true', required=False, default=False)
    args = parser.parse_args()
    print('#######################################\n')

    # Activate the debuguer for kafka if -t is passsed on launch
    if args.wants_debug:
        print("Logging Debuger ON")
        # delay in order for the user to notice that the debuger is on
        time.sleep(1)
        # code for debuging that shows logs from kafka
        import logging
        logger = logging.getLogger('kafka')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)

    # Execute a kinit command to get a new kerberos ticket if -k is passed on launch
    if args.kerberos_ticket:
        print(" Execute kinit process to get kerberos authentication ticket ")

    # List all the topics for the given groupid if -t is passed on launch
    if args.wants_list_topics:
        listtopics("show")

    # Print in the command prompt the state of the connection and the partition number for the given topic if -p is passed on launch
    if args.wants_partitions:
        print(" Connection to ", BOOTSTRAP_SERVER, " : ", consumer.bootstrap_connected())
        print(" Partition ", getpartition(KAFKA_TOPIC))

    # Print in the command prompt the beginning and en offset for the given topic if -so is passed on launch
    if args.seek_to_beginning:
        print(' --- Earliest Offset : ', getoffsets(KAFKA_TOPIC, 'beginning'))
        print(' --- Latest Offset : ', getoffsets(KAFKA_TOPIC, 'end'))

    # Print in the command prompt the offset updates for all the topics available for the given group if -cu is passed on launch (need ./topics.json to work)
    if args.check_topics_upates:
        if not os.path.isfile('./topics.json'):
            quit("No ./topics.json file founded, You first need to create one with '-t' argument")
        listtopicsold = {}
        listtopicsnew = set(consumer.topics())
        i = 0
        for line in open('./topics.json', 'r'):
            listtopicsold["line " + str(i)] = json.loads(line)
            i = i + 1
        i = 0
        newchanges = False
        for key in listtopicsold:
            for topic in listtopicsnew:
                if listtopicsold["line " + str(i)]["topic"]["name"] == topic:
                    newbeginningoffset = getoffsets(topic, 'beginning')
                    newendoffset = getoffsets(topic, 'end')
                    if not listtopicsold["line " + str(i)]["topic"]["beginning"] == newbeginningoffset:
                        print(" --- New beginning offset: ", newbeginningoffset, " for topic: ", topic)
                        newchanges = True
                    if not listtopicsold["line " + str(i)]["topic"]["end"] == newendoffset:
                        print(" --- New Records at end offset: ", newendoffset, " for topic: ", topic)
                        newchanges = True
            i = i + 1
        if newchanges is True:
            listtopics("hide")

    print('\n#######################################')


def countrecords(filename):
    """
    # Goal: count the number of records (lines) in the given file and print the result in the command prompt
    # Input: filename (path and name of the file)
    # Output: Nothing
    """
    with open(filename, "r") as outfile:
        count = 0
        for count, line in enumerate(outfile):
            pass
        print('Total records acquired :', count)
    outfile.close()


"""
This next part of the library focuses on functions which can be used in a python script, instead of the previous ones which 
focused more on functions for command prompt run of this library as a main file. This means that the function from this next 
part can be imported for use in another python file.
"""


def initialising_kerberos_ticket(key_path: str,
                                 principal_name: str,
                                 length_kerberos_ticket: int = 1) -> subprocess:
    """
    Goal: this function initialises the kerberos ticket
    Input: key path (path and name of the file, .key), principal name (username), length of the kerberos ticket (int days, >=1 and <=6)
    Output: Nothing
    """
    if length_kerberos_ticket > 6 or length_kerberos_ticket < 1:
        print(
            'Length of ticket must be greater or equal to 1 day (int 1) and smaller or equal to 6 days (int 6). Default is 1.')
    else:
        subprocess.call("kinit -V -l " + str(length_kerberos_ticket) + "d -k -t " + key_path + " " + principal_name)


def default_post_analyses_function(file_name, lst: list) -> list:
    """
    Goal: default function used to create a file with data list
    Input: file name, data list
    Output: file created (+written) lst and 
    """
    with open(file_name, 'w') as f:
        for i in lst:
            f.write(str(i) + '\n')
    return lst


def basic_kafka_consumer_schema_stream(schema_registry_link: str,
                                       Username: str,
                                       Password: str,
                                       Topic: str,
                                       bootstrap_server: str,
                                       GroupID: str,
                                       auto_commit: str,
                                       when_to_get_data: str,
                                       certificat_path: str,
                                       pre_time_out_func_variables: list = '', #CHANGE
                                       pre_time_out_func: 'function' = lambda Nothing : [],
                                       func: 'function' = lambda msg_value,lst: lst.append(msg_value),
                                       after_time_out_func: 'function' = default_post_analyses_function,
                                       consumer_timeout: int = 100000,
                                       security_proto: str = "SASL_SSL",
                                       sasl_mechan: str = "GSSAPI",
                                       ssl_check_host: str = 'false',
                                       file_name: str = 'kafka_stream_output.txt') -> bool:
    """
    Goal: this function starts a kafkaconsumer and gets the kafka data.
    Input: kafka consumer configuration + schema registry access configuration + configuration of analyses file
    Output: output of kafka stream 
    """
    kafka_consumer = initialising_kafka_consumer(Topic,
                                                 bootstrap_server,
                                                 GroupID,
                                                 auto_commit,
                                                 when_to_get_data,
                                                 certificat_path,
                                                 consumer_timeout,
                                                 security_proto,
                                                 sasl_mechan,
                                                 ssl_check_host
                                                 )
    deserialiser = schema_registry_deserialiser(Username,
                                                Password,
                                                schema_registry_link,
                                                Topic)
    kafka_stream_output = get_kafka_stream(kafka_consumer,
                                           deserialiser,
                                           pre_time_out_func,
                                           pre_time_out_func_variables,
                                           func,
                                           after_time_out_func,
                                           file_name)
    return kafka_stream_output


def initialising_kafka_consumer(Topic: str,
                                bootstrap_server: str,
                                GroupID: str,
                                auto_commit: str,
                                when_to_get_data: str,
                                certificat_path: str,
                                consumer_timeout: int = 100000,
                                security_proto: str = "SASL_SSL",
                                sasl_mechan: str = "GSSAPI",
                                ssl_check_host: str = 'false'
                                ) -> KafkaConsumer:
    """
    Goal: this function initialises a Kafka consumer
    Input: kafka consumer configuration 
    Output: kafka consumer
    """
    consumer = KafkaConsumer(Topic,
                             bootstrap_servers=bootstrap_server,
                             group_id=GroupID,
                             enable_auto_commit=auto_commit,
                             auto_offset_reset=when_to_get_data,
                             ssl_check_hostname=ssl_check_host,
                             ssl_cafile=certificat_path,
                             security_protocol=security_proto,
                             sasl_mechanism=sasl_mechan,
                             consumer_timeout_ms=consumer_timeout, )  # times out after 10 seconds
    return consumer


def schema_registry_deserialiser(schema_registry_user_name: str,
                                 schema_registry_password: str,
                                 schema_registry_link: str,
                                 Topic: str) -> AvroKeyValueSerde:
    """
    Goal: this function creates the deserialiser for the schema registry
    Input: schema registry acess configuration 
    Output: deserialiser object
    """
    registry_client = SchemaRegistry(
        schema_registry_link,
        HTTPBasicAuth(schema_registry_user_name, schema_registry_password),
        headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
    )
    avroSerde = AvroKeyValueSerde(registry_client, Topic)
    return avroSerde


def get_kafka_stream(kafka_consumer: object,
                     deserialiser: object,
                     pre_time_out_func: 'function',
                     pre_time_out_func_variables: list,
                     func: 'function',
                     after_time_out_func: 'function',
                     file_name: str) -> bool:
    """
    Goal: this is the function which reads the kafka broker and gets data
    Input: kafka consumer, deserialiser, initialising function, analyses function, saving function (post analysis)
    Output: stream output (data which was saved in the saving function)
    """
    item = pre_time_out_func(pre_time_out_func_variables)
    for msg in kafka_consumer:
        v = deserialiser.value.deserialize(msg.value)
        item = func(v, item)
    kafka_consumer.close()
    output = after_time_out_func(file_name, item)
    return output

# Condition executed if this is the main python file
if __name__ == '__main__':
    
    # Execute a kinit command to get a new kerberos ticket if -k is passed on launch (need to be done before launching the kafka consumer)
    if len(sys.argv) > 1:
        if sys.argv[1] == "-k":
            kerbcmd = 'kinit -V -l 6d -k -t {0} {1}'.format(KEYTAB, PINCIPAL_NAME)
            runwincmd(kerbcmd) 
    
    # Initialise kafka consumer and schema registry and avro serd
    consumer = kafkaconsumer()
    registry_client = schemaregistry()
    avroSerde = avroserde(registry_client, KAFKA_TOPIC)

    # Initialize all arguments parser
    if len(sys.argv) > 1: arguments()
    end_offsets = getoffsets(KAFKA_TOPIC, 'end')
    beginning_offsets = getoffsets(KAFKA_TOPIC, 'beginning')

    # Create dir, file and clean it if exist
    filename = "./records/{0}.json".format(KAFKA_TOPIC)
    preparefile(filename)

    # Main loop to print and deserialize messages
    while True:
        print("Consumer Started ! \nWaiting for records...")
        try:
            msg = [{'offset': ''}]
            for msg in consumer:
                # Deserializing keys and values
                value = avroSerde.value.deserialize(msg.value)
                key = avroSerde.key.deserialize(msg.key)
                # Printing keys and values to cli
                print(msg.offset, msg.partition, key, value)
                if end_offsets - 1 == msg.offset:
                    break
                # Converting records to json and writing them in a file
                dic = {"key": key, "value": value}
                writejson(dic, filename)
        # Stop the consumer if the user interrupt with ctrlC or ctrlZ
        except KeyboardInterrupt:
            print("Consumer Stoped !")
            break
        # Stop teh consumer if we reach the end offset for the given partition
        if end_offsets == beginning_offsets or msg == None or end_offsets - 1 == msg.offset:
            print("No new records !")
            countrecords(filename)
            break
    # exit the code
    consumer.close()
    quit("Consumer Closed !")




