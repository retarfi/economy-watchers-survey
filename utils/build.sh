cd $(dirname $0)/..
huggingface-cli download retarfi/economy-watchers-survey --local-dir hf --repo-type dataset --local-dir-use-symlinks=False

array=("current" "future")
TEST_SAMPLES=15000
EVALTEST_SAMPLES=30000
TEST_FILES=-1
EVALTEST_FILES=-1

# Prepare
for DIRECTORY in ${array[@]}
do
    ALL_SAMPLES=`jq -s 'add | length' data/$DIRECTORY/*.json`
    ALL_FILES=`find data/$DIRECTORY/ -name "*.json" | sort -r`
    i=1
    SAMPLES_TMP=0
    DO_FOR_TEST=1
    while :
    do
        FNAME=`echo $ALL_FILES | cut -d ' ' -f $i`
        N=`cat  $FNAME | jq 'length'`
        SAMPLES_TMP=`echo "$SAMPLES_TMP+$N" | bc`
        if [ $SAMPLES_TMP -ge $TEST_SAMPLES ] && [ $DO_FOR_TEST -eq 1 ] && [ $i -ge $TEST_FILES ]
        then
            TEST_FILES=$i
            DO_FOR_TEST=0
        fi
        if [ $SAMPLES_TMP -ge $EVALTEST_SAMPLES ]
        then
            if [ $i -ge $EVALTEST_FILES ]
            then
                EVALTEST_FILES=$i
            fi
            break
        fi
        i=`echo "$i+1" | bc`
    done
done

# Build
for DIRECTORY in ${array[@]}
do
    jq -s add `find data/$DIRECTORY/ -name "*.json" | sort | head -n -$EVALTEST_FILES` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/$DIRECTORY/train.jsonl
    jq -s add `find data/$DIRECTORY/ -name "*.json" | sort | tail -n $EVALTEST_FILES | head -n -$TEST_FILES` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/${DIRECTORY}/validation.jsonl
    jq -s add `find data/$DIRECTORY/ -name "*.json" | sort | tail -n $TEST_FILES` | jq -n -c --stream 'fromstream(1|truncate_stream(inputs))' > hf/${DIRECTORY}/test.jsonl
done
