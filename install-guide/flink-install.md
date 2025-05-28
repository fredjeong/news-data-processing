# Flink 설치

- [Java 설치 (이미 설치되었을 경우 무시)](./java-install.md)

```bash
cd Desktop
wget https://downloads.apache.org/flink/flink-1.20.0/flink-1.20.0-bin-scala_2.12.tgz
tar -xzf flink-1.20.0-bin-scala_2.12.tgz
mv flink-1.20.0 flink
rm flink-1.20.0-bin-scala_2.12.tgz

echo 'export FLINK_HOME=~/Desktop/flink' >> ~/.zshrc
echo 'export PATH=$PATH:$FLINK_HOME/bin' >> ~/.zshrc
source ~/.zshrc
```

# Flink 실행

```bash
$FLINK_HOME/bin/start-cluster.sh
$FLINK_HOME/bin/stop-cluster.sh

$FLINK_HOME/bin/flink run -py skeleton.py
```