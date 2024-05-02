cd $(dirname $0)/..
huggingface-cli download retarfi/economy-watchers-survey --local-dir hf --repo-type dataset --local-dir-use-symlinks=False

TEST_RATIO=0.1
NUM_JSON=`ls -F data/current/ | grep -v / | wc -l`
NUM_TEST=`echo "($NUM_JSON-23)*$TEST_RATIO" | bc | awk '{printf("%d\n", $1 + 0.5)}'`
jq -s add `find data/current/ -name "*.json" | sort | head -n -$NUM_TEST` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/current/train.jsonl
jq -s add `find data/current/ -name "*.json" | sort | tail -n $NUM_TEST` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/current/test.jsonl
NUM_JSON=`ls -F data/future/ | grep -v / | wc -l`
NUM_TEST=`echo "($NUM_JSON-46)*$TEST_RATIO" | bc | awk '{printf("%d\n", $1 + 0.5)}'`
jq -s add `find data/future/ -name "*.json" | sort | head -n -$NUM_TEST` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/future/train.jsonl
jq -s add `find data/future/ -name "*.json" | sort | tail -n $NUM_TEST` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/future/test.jsonl
