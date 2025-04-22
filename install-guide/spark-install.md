# Spark 설치

- [Java 설치 (이미 설치되었을 경우 무시)](./java-install.md)

```bash
cd Desktop
wget https://archive.apache.org/dist/spark/spark-3.5.4/spark-3.5.4-bin-hadoop3.tgz
tar -xzf spark-3.5.4-bin-hadoop3.tgz
mv spark-3.5.4-bin-hadoop3 spark
rm spark-3.5.4-bin-hadoop3.tgz

echo 'export SPARK_HOME=~/Desktop/spark' >> ~/.zshrc
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.zshrc
source ~/.zshrc

cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh
chmod +x $SPARK_HOME/conf/spark-env.sh

echo 'export SPARK_MASTER_WEBUI_PORT=8082' >> ~/.zshrc
echo 'export SPARK_MASTER_HOST=0.0.0.0' >> ~/.zshrc
echo 'export SPARK_LOCAL_IP=0.0.0.0' >> ~/.zshrc
source ~/.zshrc
```

# Spark 실행 (standalone 클러스터 모드 사용)

```bash
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077
jps
$SPARK_HOME/sbin/stop-master.sh
$SPARK_HOME/sbin/stop-worker.sh
```