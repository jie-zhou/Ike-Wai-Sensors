#!/bin/bash
#get filename argument

while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -f|--filename)
    FILENAME="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done
#set the current date
DATE=$(date '+%Y-%m-%d')

#create folder with todays data if it doesn't exist
curl -# -k -H "Authorization: Bearer 4d197a543681b336b817f951f998e64" -X PUT -d "action=mkdir&path=dropsensor_data/$DATE" 'https://ikeauth.its.hawaii.edu/files/v2/media/'

#upload file
curl -# -k -H "Authorization: Bearer 4d197a543681b336b817f951f998e64" -X POST -F "fileToUpload=@$FILENAME" "https://ikeauth.its.hawaii.edu/files/v2/media/system/mydata-tamrako/dropsensor_data/$DATE"
