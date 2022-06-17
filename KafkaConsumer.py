#######################################
######## MAIN CODE FOR PROD ENV #######
#######################################
# Libraries
import datetime
import sys, os
import time  # Used for delays
import configparser  # Used for configfile.ini
import argparse  # Libraries for passing arguments when lanching pyhton code
import json  # Used to treat json objects and files
import subprocess  # Used to exec windows cmd
from kafka import KafkaConsumer, TopicPartition
from confluent_avro import AvroKeyValueSerde, SchemaRegistry
from confluent_avro.schema_registry import HTTPBasicAuth

Config = configparser.ConfigParser()
if not os.path.isfile("configuration.ini"): quit(
    "Configuration file needed ! No configuration.ini files found in the current directory")
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
    # code for configuring the kafka consumer with kerberos and ssl cert
    consumer = KafkaConsumer(KAFKA_TOPIC,
                             bootstrap_servers=BOOTSTRAP_SERVER,
                             group_id=GROUP_ID,
                             enable_auto_commit=False,  # if set to true means you can receive the records only once
                             auto_offset_reset=AUTO_OFFSET_RESET,
                             ssl_check_hostname=False,
                             ssl_cafile=SSL_CAFILE,
                             security_protocol=SECURITY_PROTOCOL,
                             sasl_mechanism=SASL_MECHANISM,
                             sasl_kerberos_service_name=SALS_KERBEROS_SERVICE_NAME,
                             consumer_timeout_ms=15000, )
    return consumer


def schemaregistry():
    # code for configuring the schema registry access
    registry_client = SchemaRegistry(
        SCHEMA_ADDRESS,
        HTTPBasicAuth(SCHEMA_USERNAME, SCHEMA_PASSWORD),
        headers={"Content-Type": "application/vnd.schemaregistry+json"}, )
    return registry_client


def avroserde(registry_client, KAFKA_TOPIC):
    avroSerde = AvroKeyValueSerde(registry_client, KAFKA_TOPIC)
    return avroSerde


def run_win_cmd(cmd):
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


def getPartition(topic):
    partition = consumer.partitions_for_topic(topic).pop()
    return partition


def getOffsets(topic, string):
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


def arguments():
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
    args = parser.parse_args()
    print('#######################################\n')
    if args.wants_debug:
        print("Logging Debuger ON")
        # delay in order for the user to notice that the debuger is on
        time.sleep(1)
        # code for debuging wich shows logs from kafka
        import logging
        logger = logging.getLogger('kafka')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.DEBUG)

    if args.kerberos_ticket:
        kerbcmd = 'kinit -V -l 6d -k -t {0} {1}'.format(KEYTAB, PINCIPAL_NAME)
        run_win_cmd(kerbcmd)
        print(" Execute kinit process to get kerberos authentication ticket ")

    if args.wants_list_topics:
        listtopics = set(consumer.topics())
        print(" List of topics for ", GROUP_ID)
        for topics in listtopics:
            print(topics)

    if args.wants_partitions:
        print(" Connection to ", BOOTSTRAP_SERVER, " : ", consumer.bootstrap_connected())
        print(" Partition ", getPartition(KAFKA_TOPIC))

    if args.seek_to_beginning:
        print(' --- Earliest Offset : ', getOffsets(KAFKA_TOPIC, 'beginning'))
        print(' --- Latest Offset : ', getOffsets(KAFKA_TOPIC, 'end'))
    print('\n#######################################')


def preparefile():
    if not os.path.isdir("./records"):
        os.mkdir("./records")
    if os.path.isfile("./records/{0}.json".format(KAFKA_TOPIC)):
        # Clean the file that will store the records
        with open(filename, "w") as outfile:
            outfile.write('')
            outfile.close()


def writeJSON(dic):
    json_object = json.dumps(dic)  # ,indent = 4
    with open(filename, "a") as outfile:
        outfile.write(json_object)
        outfile.write("\n")
        outfile.close()


# Condition executed if it is the main python file
if __name__ == '__main__':

    # Initialise kafka consumer and schema registry and avro serd
    consumer = kafkaconsumer()
    registry_client = schemaregistry()
    avroSerde = avroserde(registry_client, KAFKA_TOPIC)

    # Initialize all arguments parser
    if len(sys.argv) > 1: arguments()
    end_offsets = getOffsets(KAFKA_TOPIC, 'end')
    beginning_offsets = getOffsets(KAFKA_TOPIC, 'beginning')

    # Create dir, file and clean it if exist
    filename = "./records/{0}.json".format(KAFKA_TOPIC)
    preparefile()

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
                dic = (key, value)
                writeJSON(dic)
        except KeyboardInterrupt:
            print("Consumer Stoped !")
            break
        if end_offsets == beginning_offsets or msg == None or end_offsets - 1 == msg.offset:
            print("No new records !")
            break

    consumer.close()
    print("Consumer Closed !")
    with open("records.json", "r") as outfile:
        count = 0
        for count, line in enumerate(outfile):
            pass
        print('Total records acquired :', count)


