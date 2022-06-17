**This is a kafka consumer python programm, wich deserialize data from an avro schema registry and access is managed by kerberos and security by ssl** 

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
- [x] fastavro==1.5.1
- [x] gssapi==1.7.3
- [x] idna==3.3
- [x] kafka==1.3.5
- [x] kafka-python==2.0.2
- [x] python-status==1.0.1
- [x] requests==2.28.0
- [x] urllib3==1.26.9
- [x] wincertstore==0.2


You can run the consumer by importing the kafka consumer python script into
your code, inputing the required fields in the function.