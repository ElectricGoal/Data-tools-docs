# Data-tools-docs

Installation document for data engineering tools: Hadoop, Spark, Hive, Presto, Kafka,...and connection between them.

## My environment

- **OS**: Ubuntu server 22.04
- **Username**: playground

## Hadoop installation

### 1. Installing Java OpenJDK

```
sudo apt install default-jdk
java -version
```

### 2. Setting SSH Authentication

```
sudo apt install openssh-server openssh-client pdsh

ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Verify SSH

```
ssh localhost
```

Enter yes to confirm and add the SSH fingerprint and you'll be connected to the server without password authentication

### 3. Downloading Hadoop

```
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xvzf hadoop-3.3.6.tar.gz
sudo mv hadoop-3.3.6 /usr/local/hadoop
sudo rm -r hadoop-3.3.6
```

### 4. Setting up Hadoop Environment

Open the configuration file `bashrc`
```
nano ~/.bashrc
```

Copy and paste the following lines to file

```
# Hadoop environment variables
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export HADOOP_YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
```

Run this command to apply new changes

```
source ~/.bashrc
```

Open `hadoop-env.sh` file

```
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

Uncomment the `JAVA_HOME`` environment line and change the value to the Java OpenJDK installation directory. Then save it

```
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

Verify Hadoop version

```
hadoop version
```

### 5. Setting Hadoop cluster in Pseudo-Distributed Mode

Hadoop cluster has three different modes:

- **Local Mode (Standalone)**: default hadoop installation, which is run as a single Java process and non-distributed mode. With this, you can easily debug the hadoop process.
- **Pseudo-Distributed Mode**: this allows you to run a hadoop cluster with distributed mode even with only a single node/server. In this mode, hadoop processes will be run in separate Java processes.
- **Fully-Distributed Mode**: large hadoop deployment with multiple or even thousands of nodes/servers. If you want to run hadoop in production, you should use the hadoop in fully-distributed mode.

#### 5.1. Setting up NameNode and DataNode

Open file `core-site.xml`

```
sudo nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

Add the following lines to file and save it

```
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://127.0.0.1:9000</value>
    </property>
</configuration>
```

Run the below commands to create new directories for NameNode and DataNode and authorize
Remember to replace **username** to your username, in my case was `playground`

```
sudo mkdir -p /home/{username}/hdfs/{namenode,datanode}
sudo chown -R {username}:{username} /home/{username}/hdfs
```

Next, open file `hdfs-site.xml`

```
sudo nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

Add the following lines to file and save it

```
<configuration>

    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>

   <property>
      <name>dfs.name.dir</name>
      <value>file:///home/{username}/hdfs/namenode</value>
   </property>

   <property>
      <name>dfs.data.dir</name>
      <value>file:///home/{username}/hdfs/datanode</value>
   </property>

</configuration>
```

Run the below command to format the hadoop filesystem

```
hdfs namenode -format
```

Run the following command to start NameNode and DataNode

```
start-dfs.sh
```

If your side encountered this error: `localhost: rcmd: socket: Permission denied `, you should do some following steps: 

- Check your pdsh default rcmd rsh:

```
pdsh -q -w localhost
```

- Modify pdsh's default rcmd to ssh

```
export PDSH_RCMD_TYPE=ssh
```

- Start dfs again

```
start-dfs.sh
```

#### 5.2. Setting up Yarn Manager

Open file `mapred-site.xml`

```
sudo nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

Add the following lines to file and save it

```
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```

Open file `yarn-site.xml`

```
sudo nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Add the following lines to file and save it

```
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
```

Run the below command to start the Yarn daemons
```
start-yarn.sh
```

Using `jps` command to chech Java process, you should see all services are started

```
jps
```

### 6. Web interface

The Hadoop NameNode web interface is running port `9870`. Open your web browser and visit the server IP address followed by port `9870` (ie: http://127.0.0.1:9870)

The ResourceManager should be running at the default port `8088`. Open your web browser and visit the server IP address followed by the ResourceManager port `8088` (i.e: http://127.0.0.1:8088).