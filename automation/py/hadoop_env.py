"""
Production-grade Fabric script for deploying a multi-node Apache Hadoop Cluster on CentOS
Author: prem = kry496@my.utsa.edu
"""

from fabric.api import env, roles, sudo, execute, put, run, local, lcd, cd, parallel, settings, quiet, hide
from fabric.contrib.files import exists, append, contains
import platform, os, logging

# Initialize logging for audit trail and monitoring
logging.basicConfig(level=logging.INFO, filename='hadoop_deploy.log', format='%(asctime)s - %(levelname)s - %(message)s')

# Hadoop Environment and General Configuration
HADOOP_VERSION = '2.7.3'
HADOOP_DIR = '/usr/local/hadoop'
HADOOP_URL = f'http://www-eu.apache.org/dist/hadoop/core/hadoop-{HADOOP_VERSION}/hadoop-{HADOOP_VERSION}.tar.gz'
JAVA_HOME = '/usr/lib/jvm/default-java'
HADOOP_CONFIG_FILES_DIR = '/temp_hadoop/hadoop_config_files'

# Node details and environment setup
env.user = 'hduser'
env.roledefs = {
    'masternode': ['192.168.56.184'],
    'slavenodes': ['192.168.56.185', '192.168.56.186', '192.168.56.187'],
}
env.roledefs['all'] = [x for y in env.roledefs.values() for x in y]

# Pre-defined updates to system files
bashrc_updates = f"""
export HADOOP_HOME={HADOOP_DIR}
export JAVA_HOME={JAVA_HOME}
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
"""

hosts_file_update = '''
192.168.56.184 master
192.168.56.185 slave1
192.168.56.186 slave2
192.168.56.187 slave3
'''

sysctl_update = '''
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
'''

test_files = [
    'http://www.gutenberg.org/cache/epub/2041/pg2041.txt',
    'http://www.gutenberg.org/files/5000/5000-8.txt',
    'http://www.gutenberg.org/files/4300/4300-0.txt'
]

# Utility functions
def _java_installation():
    distro = platform.platform().lower()
    try:
        if 'ubuntu' in distro:
            sudo('apt-get -y install default-jdk')
        elif 'centos' in distro:
            sudo('yum install -y java-1.8.0-openjdk')
        else:
            logging.error("Unsupported distribution. Exiting...")
            print('Unsupported distribution. Exiting...')
            exit()
    except Exception as e:
        logging.error(f"Java installation failed: {e}")
        raise

# Parallel execution for Java installation
@parallel
@roles('all')
def install_java():
    with quiet():
        if run('which java', warn_only=True).failed:
            logging.info("Java not found, proceeding with installation.")
            _java_installation()
        else:
            logging.info('Java is already installed.')

@parallel
@roles('all')
def create_hduser():
    try:
        if run('id -u hduser', warn_only=True).failed:
            sudo('addgroup hadoopadmin && adduser --ingroup hadoopadmin hduser && usermod -aG sudo hduser', pty=True)
            logging.info("Created hduser and added to sudo group.")
    except Exception as e:
        logging.error(f"Failed to create hduser: {e}")
        raise

@parallel
@roles('all')
def update_bashrc():
    try:
        if exists('/home/hduser/.bashrc'):
            if not contains('/home/hduser/.bashrc', "HADOOP"):
                append('/home/hduser/.bashrc', bashrc_updates, use_sudo=True)
                sudo('source /home/hduser/.bashrc', pty=True)
                logging.info("Updated .bashrc for hduser with Hadoop and Java paths.")
    except Exception as e:
        logging.error(f"Failed to update .bashrc: {e}")
        raise

@roles('all')
def update_hosts_file():
    try:
        if not contains('/etc/hosts', 'master'):
            append('/etc/hosts', hosts_file_update, use_sudo=True)
            logging.info("Updated /etc/hosts file for Hadoop cluster.")
    except Exception as e:
        logging.error(f"Failed to update hosts file: {e}")
        raise

@parallel
@roles('all')
def disable_ipv6():
    try:
        if not contains('/proc/sys/net/ipv6/conf/all/disable_ipv6', '1'):
            append('/etc/sysctl.conf', sysctl_update, use_sudo=True)
            sudo('sysctl -p', pty=True)
            logging.info("IPv6 disabled across all nodes.")
    except Exception as e:
        logging.error(f"Failed to disable IPv6: {e}")
        raise

@parallel
@roles('all')
def download_hadoop():
    try:
        if not exists(f'{HADOOP_DIR}/hadoop-{HADOOP_VERSION}.tar.gz'):
            sudo(f'mkdir -p {HADOOP_DIR}', pty=True)
            sudo(f'chown hduser:hadoopadmin {HADOOP_DIR}', pty=True)
            with cd(HADOOP_DIR):
                run(f'wget {HADOOP_URL}')
                sudo(f'tar xzf hadoop-{HADOOP_VERSION}.tar.gz', pty=True)
                sudo(f'mv hadoop-{HADOOP_VERSION} hadoop', pty=True)
                logging.info("Hadoop downloaded and extracted.")
    except Exception as e:
        logging.error(f"Failed to download or extract Hadoop: {e}")
        raise

@roles('masternode')
def download_test_files():
    test_dir = '/home/hduser/test'
    try:
        if not exists(test_dir):
            sudo(f'mkdir -p {test_dir}', user='hduser', pty=True)
            with cd(test_dir):
                for url in test_files:
                    run(f'wget {url}')
            logging.info("Downloaded test files for MapReduce.")
    except Exception as e:
        logging.error(f"Failed to download test files: {e}")
        raise

@parallel
@roles('all')
def configure_hadoop():
    try:
        with lcd(HADOOP_CONFIG_FILES_DIR):
            config_files = ['hadoop-env.sh', 'core-site.xml', 'hdfs-site.xml', 'mapred-site.xml', 'yarn-site.xml', 'slaves']
            for config_file in config_files:
                put(config_file, f'{HADOOP_DIR}/hadoop/etc/hadoop/{config_file}')
            logging.info("Hadoop configuration files deployed.")
    except Exception as e:
        logging.error(f"Failed to configure Hadoop: {e}")
        raise

@roles('masternode')
def format_namenode():
    try:
        with cd(f'{HADOOP_DIR}/hadoop/bin'):
            run('./hadoop namenode -format', pty=True)
            logging.info("Hadoop namenode formatted successfully.")
    except Exception as e:
        logging.error(f"Failed to format namenode: {e}")
        raise

@roles('masternode')
def start_hadoop():
    try:
        with cd(f'{HADOOP_DIR}/hadoop/sbin'):
            sudo('./start-all.sh', user='hduser', pty=True)
            sudo('./mr-jobhistory-daemon.sh start historyserver', user='hduser', pty=True)
            logging.info("Hadoop services started on master node.")
    except Exception as e:
        logging.error(f"Failed to start Hadoop services: {e}")
        raise

@roles('masternode')
def test_mapreduce():
    try:
        with cd(f'{HADOOP_DIR}/hadoop/bin'):
            run(f'./hdfs dfs -copyFromLocal /home/hduser/test /a')
            run(f'./hadoop jar {HADOOP_DIR}/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-{HADOOP_VERSION}.jar wordcount /a /y')
            logging.info("MapReduce job executed successfully.")
    except Exception as e:
        logging.error(f"Failed to execute MapReduce job: {e}")
        raise

@roles('masternode')
def verify_mapreduce():
    try:
        with cd(f'{HADOOP_DIR}/hadoop/bin'):
            run('./hdfs dfs -ls /y')
            logging.info("MapReduce output verified.")
    except Exception as e:
        logging.error(f"Failed to verify MapReduce output: {e}")
        raise

@roles('masternode')
def stop_hadoop():
    try:
        with cd(f'{HADOOP_DIR}/hadoop/sbin'):
            sudo('./stop-all.sh', user='hduser', pty=True)
            sudo('./mr-jobhistory-daemon.sh stop historyserver', user='hduser', pty=True)
            logging.info("Hadoop services stopped.")
    except Exception as e:
        logging.error(f"Failed to stop Hadoop services: {e}")
        raise

# Main deploy function
def deploy():
    try:
        execute(create_hduser)
        execute(update_hosts_file)
        execute(install_java)
        execute(update_bashrc)
        execute(disable_ipv6)
        execute(download_hadoop)
        execute(download_test_files)
        execute(configure_hadoop)
        execute(format_namenode)
        execute(start_hadoop)
        execute(test_mapreduce)
        execute(verify_mapreduce)
        execute(stop_hadoop)
        logging.info("Deployment completed successfully.")
    except Exception as e:
        logging.critical(f"Deployment failed: {e}")
        raise
