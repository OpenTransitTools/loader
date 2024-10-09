# keep running the bundle of curls (curl_runner executes 30 trips right now)
date; for n in {1..5555}; do SECONDS=0; curl_runner.sh > /dev/null 2>&1; echo run $n took $SECONDS secs; done

# mac gdate with milliseconds
date; for n in {1..5555}; do SECONDS=0; curl_runner.sh > /dev/null 2>&1; gdate +"%T.%2N"; echo run $n took $SECONDS secs; done

