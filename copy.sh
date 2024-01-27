files=(../Artemka123/$1.[0-9].*)

for dirName in "${files[@]}"
do
    taskNum=${dirName##*/}
    echo "making directory $taskNum"
    mkdir $taskNum
    echo "copying $taskNum from $dirName in python-SDA/$taskNum"
    cp -r $dirName/tasks $taskNum/tasks
done

