# Kafka 설치

- [Java 설치 (이미 설치되었을 경우 무시)](./java-install.md)

```bash
cd Desktop
wget https://dlcdn.apache.org/kafka/3.9.0/kafka_2.12-3.9.0.tgz
tar -xzf kafka_2.12-3.9.0.tgz
mv kafka_2.12-3.9.0 kafka
rm kafka_2.12-3.9.0.tgz

echo 'export KAFKA_HOME=~/Desktop/kafka' >> ~/.zshrc
echo 'export PATH=$PATH:$KAFKA_HOME/bin' >> ~/.zshrc
source ~/.zshrc
```

# Kafka 실행

```bash
$KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
$KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties
```
