# Data-tools-docs

Installation document for data engineering tools: Hadoop, Spark, Hive, Presto and the connection between them.

## My environment

- **OS**: Ubuntu server 22.04
- **Username**: playground

## Hadoop installation

### 1. Installing Java OpenJDK

Should not install Java 11 version becasue HIVE is not compatible with it

```
sudo apt install openjdk-8-jdk
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
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
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
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
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
![jps](/imgs/jps.png)

### 6. Web interface

The Hadoop NameNode web interface is running port `9870`. Open your web browser and visit the server IP address followed by port `9870` (ie: http://127.0.0.1:9870)

The ResourceManager should be running at the default port `8088`. Open your web browser and visit the server IP address followed by the ResourceManager port `8088` (i.e: http://127.0.0.1:8088).

## Spark installation

### 1. Downloading Spark

```
wget https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz

tar -xvzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /usr/local/spark
sudo rm -r spark-3.5.0-bin-hadoop3
```

### 2. Setting up Spark environment

Open the configuration file

```
nano ~/.bashrc
```

Add the following line and save it

```
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
```

Run this command to apply new changes

```
source ~/.bashrc
```

### 3. Verifing installation

Run this command, you should see Spark shell with logo

```
spark-shell
```

Download this repo and run spark-submit with `ingestion.py` file

```
spark-submit ingestion.py
```

If you did not see any errors, your installation is complete.

You could see a parquest file in HDFS web interface

![ingestion](/imgs/hdfs_ingestion.png)

## Hive installation

### 1. Downloading Hive

```
wget https://apache.osuosl.org/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz
tar -xzf apache-hive-3.1.3-bin.tar.gz
mv apache-hive-3.1.3 /usr/local/hive
```

### 2. Setting up Hive environment

Append Hive environment variables to `.bashrc` file and save it

```
export HIVE_HOME=/home/prabha/hive
export PATH=$PATH:$HIVE_HOME/sbin:$HIVE_HOME/bin
export CLASSPATH=$CLASSPATH:$HADOOP_HOME/lib/*:$HIVE_HOME/lib/*
```

Run this command to apply new changes

```
source ~/.bashrc
```

### 3. Installing MySQL and configure it as Hive metastore

Install with the command below

```
sudo apt-get install mysql-server
```

Go to mysql terminal (use root as password)

```
sudo mysql -u root -p
```

In mysql terminal, run these command in order:
- CREATE DATABASE metastore_db;
- CREATE USER 'hiveusr'@'%' IDENTIFIED BY 'hivepassword';
- GRANT all on *.* to 'hiveusr'@'%';
- flush privileges;
- exit;

Note that you can change your mysql username and password

Install mysql connector and copy connection jar file to hive lib

```
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.3.0.tar.gz

tar -xvf mysql-connector-j-8.3.0.tar.gz 

cd mysql-connector-j-8.3.0/

sudo cp mysql-connector-j-8.3.0.jar $HIVE_HOME/lib/
```

After that, remove `log4j-slf4j-impl-2.17.1.jar` file in `$HIVE_HOME/lib/` to prevent duplicated error

```
sudo rm log4j-slf4j-impl-2.17.1.jar
```

### 4. Edit Hive configuration

Create some HDFS folders

```
hdfs dfs -mkdir -p /user/hive/warehouse

hdfs dfs -mkdir -p /tmp/hive

hdfs dfs -chmod g+w /user/tmp
hdfs dfs -chmod g+w /user/hive/warehouse
```

Go to `conf` folder, copy and edit `hive-site.xml`

```
cd $HIVE_HOME/conf
cp hive-default.xml.template hive-site.xml
sudo nano hive-site.xml
```

In `hive-site.xml`

- Replacing all occurrences of `${system:user.name}` to your username
- Replacing all occurrences of `${system:java.io.tmpdir}` to `/tmp/hive`. This is the location Hive stores all it’s temporary files.
- Searching `javax.jdo.option.ConnectionURL` and change its value to `jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true`

```
<name>javax.jdo.option.ConnectionURL</name> 
<value>jdbc:mysql://localhost/metastore_db?createDatabaseIfNotExist=true</value> 
```

- Searching `javax.jdo.option.ConnectionUserName` and change its value to mysql username, in my case was `hiveusr`

```
<name>javax.jdo.option.ConnectionUserName</name> 
<value>hiveusr</value>
```

- Searching `javax.jdo.option.ConnectionPassword` and change its value to mysql username, in my case was `hivepassword`

```
<name>javax.jdo.option.ConnectionPassword</name> 
<value>hivepassword</value> 
```

- Searching `javax.jdo.option.ConnectionDriverName` and change its value to `com.mysql.cj.jdbc.Driver`

```
<name>javax.jdo.option.ConnectionDriverName</name> 
<value>com.mysql.jdbc.Driver</value>
```

- Searching `&#8` and remove it if it had

Then, copy and edit `hive-env.sh`

```
cd $HIVE_HOME/conf
cp hive-env.sh.template hive-env.sh
sudo nano hive-env.sh
```

Append the below line to `hive-env.sh`

```
export HADOOP_HOME=/usr/local/hadoop
```

### 5. Verifying installation

```
cd $HIVE_HOME/bin
hive
```
You should see the below result

![hive](/imgs/hive.png)

## Presto Installation

### 1. Downloading Presto server

```
wget https://repo1.maven.org/maven2/com/facebook/presto/presto-server/0.285/presto-server-0.285.tar.gz

tar -xzf presto-server-0.285.tar.gz
mv ./presto-server-0.285 ./presto-server
```

### 2. Configuration

Create folder named `data` outside of `presto-server` folder, this folder uses to save log, metadata,...

```
mkdir data
```

Create folder named `etc` inside of `presto-server` folder

```
cd presto-server
mkdir etc
cd etc
```

Adding some configuration files with these contents

- node.properties: replacing < your-data-folder > to the path of data folder you created before

```
node.environment=production
node.id=ffffffff-ffff-ffff-ffff-ffffffffffff
node.data-dir=<your-data-folder>
```

- config.properties

```
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
query.max-memory=5GB
query.max-memory-per-node=1GB
discovery-server.enabled=true
discovery.uri=http://127.0.0.1:8080
```

- log.properties

```
com.facebook.presto = INFO
```

- jvm.config

```
-server
-Xmx16G
-XX:+UseG1GC
-XX:G1HeapRegionSize=32M
-XX:+UseGCOverheadLimit
-XX:+ExplicitGCInvokesConcurrent
-XX:+HeapDumpOnOutOfMemoryError
-XX:+ExitOnOutOfMemoryError
-Djdk.attach.allowAttachSelf=true
```

Next, create folder named `catalog` inside `etc` folder

```
mkdir catalog
cd catalog
```
Adding some configuration files with these contents

- jmx.properties

```
connector.name = jmx
```

- hive.properties

```
connector.name = hive-hadoop2
hive.metastore.uri = thrift://localhost:9083
```

### 3. Start presto server

```
cd ../../

sudo bin/launcher run
```

You should see this screen

![presto-server](/imgs/presto-server.png)

If you want to run in background, you can you this command `sudo bin/launcher start` instead

### 4. Downloading Presto client

```
wget https://repo1.maven.org/maven2/com/facebook/presto/presto-cli/0.285/presto-cli-0.285-executable.jar

sudo mv presto-cli-0.285-executable.jar presto
chmod +x presto
```

### 5. Connecting to Hive

Open to new terminal and start hive metastore service
```
hive --servvice metastore
```

Back to Presto client and run this command

```
./presto --server 127.0.0.1:8080 --catalog hive --schema test
```
![presto-cli](/imgs/presto-cli.png)

You can use `presto://127.0.0.1:8080/hive` as connection string