SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

if [ "$#" -eq 0 ];then
    find "${SCRIPTPATH}/tmp/download" -type f -name "*.xlsx"
    find "${SCRIPTPATH}/tmp/fake-storage" -type f -name "*.xlsx"
fi

if [ "$1" = "clear" ];then
    find "${SCRIPTPATH}/tmp/download" -type f -name "*.xlsx" -exec rm -f {} \;
    find "${SCRIPTPATH}/tmp/fake-storage" -type f -name "*.xlsx" -exec rm -f {} \;
fi
