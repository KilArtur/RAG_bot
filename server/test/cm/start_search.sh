docker pull docker.elastic.co/elasticsearch/elasticsearch:8.10.2
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms2g -Xmx2g" \
  -e ELASTIC_PASSWORD="password" \
  docker.elastic.co/elasticsearch/elasticsearch:8.10.2
