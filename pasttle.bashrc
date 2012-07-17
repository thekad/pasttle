#!/bin/bash

SW_VERSION="0.5"

function gettle() {
#   default values
    encrypt="yes";
    filename="-";
    verbose="no";
    insecure="no";

    version="gettle/${SW_VERSION}/curl/$( curl --version | head -1 | cut -d\  -f2- )";
#   load user preferences
    test -f ~/.pasttlerc
    if [ 0 -eq $? ];
    then
        echo "Loading ~/.pasttlerc" >> /dev/stderr
        source ~/.pasttlerc;
    fi;

    usage="\n
    USAGE\n\n
    gettle [options] -e <entry number>\n\n
    OPTIONS\n\n
        -a  API URL, this is, the root URL of the service\n\n
        -n  Do not encrypt your password before sending it\n\n
        -p 'PASSWORD' If the entry is password-protected\n\n
        -f 'FILENAME' (OPTIONAL) Output the content to the given file\n\n
        -i (OPTIONAL) If you want to skip on SSL errors\n\n
        -v (OPTIONAL) Print verbose output\n\n
    "

#   load runtime options
    OPTIND=1;
    while getopts ":a:np:f:hvie:" flag;
    do
        case $flag in
            h)
                echo -e $usage;
                return 0;
                ;;
            a) 
                apiurl="$OPTARG"
                ;;
            n)
                encrypt="no"
                ;;
            p)
                password="$OPTARG"
                ;;
            f)
                filename="$OPTARG"
                ;;
            v)
                verbose="yes"
                ;;
            i)
                insecure="yes"
                ;;
            e)
                entry="$OPTARG"
                ;;
            \?)
                echo "Invalid option: -${flag}"
                ;;
            :)
                echo "Option -${flag} requires an argument"
                ;;
        esac;
    done;

    if [ -z "$entry" ];
    then
        echo "Tell me what entry you want";
        return 1;
    fi;

    if [ -z "$apiurl" ];
    then
        echo "You don't have any apiurl in ~/.pasttlerc or missing -a parameter";
        return 1;
    else
        if [ "yes" == "$verbose" ];
        then
            echo "API URL is ${apiurl}";
        fi;
    fi;

    command="curl -A '${version}'"

    if [ ! -z "$password" ];
    then
        if [ "yes" == "$encrypt" ];
        then
            finalpass=$( echo -n "${password}" | sha1sum | cut -c 1-40 );
            if [ "yes" == "$verbose" ];
            then
                echo "echo -n '${password}' | sha1sum | cut -c 1-40 # == ${finalpass}";
            fi;
            command="${command} -d 'is_encrypted=yes'";
        else
            finalpass="$password"
        fi;
        command="${command} -d 'password=${finalpass}'";
    fi;

    if [ "yes" == "$insecure" ];
    then
        command="${command} --insecure";
    fi;

    command="${command} -o${filename} ${apiurl}/raw/${entry}";

    if [ "yes" == "$verbose" ];
    then
        command="${command} -v";
        echo $command;
    fi;

    eval $command;
    echo;
}

function pasttle() {
#   default values
    encrypt="yes";
    filename="-";
    verbose="no";
    insecure="no";

    version="pasttle/${SW_VERSION}/curl/$( curl --version | head -1 | cut -d\  -f2- )";
#   load user preferences
    test -f ~/.pasttlerc
    if [ 0 -eq $? ];
    then
        echo "Loading ~/.pasttlerc" >> /dev/stderr
        source ~/.pasttlerc;
    fi;

    usage="\n
    USAGE\n\n
    cat 'filename.ext' | pasttle [options]\n\n
    or\n\n
    pasttle -f 'filename.ext' [options]\n\n
    OPTIONS\n\n
        -a  API URL, this is, the root URL of the service\n\n
        -n  Do not encrypt your password before sending it\n\n
        -p 'PASSWORD' If you want to protect this entry with a password\n\n
        -f 'FILENAME' (OPTIONAL) Upload the given plain-text file\n\n
        -i (OPTIONAL) If you want to skip on SSL errors\n\n
        -v (OPTIONAL) Print verbose output\n\n
    "

#   load runtime options
    OPTIND=1;
    while getopts ":a:s:np:f:hvi" flag;
    do
        case $flag in
            h)
                echo -e $usage;
                return 0;
                ;;
            a) 
                apiurl="$OPTARG"
                ;;
            s) 
                syntax="$OPTARG"
                ;;
            n)
                encrypt="no"
                ;;
            p)
                password="$OPTARG"
                ;;
            f)
                filename="$OPTARG"
                ;;
            v)
                verbose="yes"
                ;;
            i)
                insecure="yes"
                ;;
            \?)
                echo "Invalid option: -${flag}"
                ;;
            :)
                echo "Option -${flag} requires an argument"
                ;;
        esac;
    done;

    if [ -z "$apiurl" ];
    then
        echo "You don't have any apiurl in ~/.pasttlerc or missing -a parameter";
        return 1;
    else
        if [ "yes" == "$verbose" ];
        then
            echo "API URL is ${apiurl}";
        fi;
    fi;

    if [ -z "$syntax" ];
    then
        syntax="${filename#*.}"
    fi;

    command="curl -A '${version}' -F 'upload=<${filename}' -F 'filename=${filename}' -F 'syntax=${syntax}'"

    if [ ! -z "$password" ];
    then
        if [ "yes" == "$encrypt" ];
        then
            finalpass=$( echo -n "${password}" | sha1sum | cut -c 1-40 );
            if [ "yes" == "$verbose" ];
            then
                echo "echo -n '${password}' | sha1sum | cut -c 1-40 # == ${finalpass}";
            fi;
            command="${command} -F 'is_encrypted=yes'";
        else
            finalpass="$password"
        fi;
        command="${command} -F 'password=${finalpass}'";
    fi;

    if [ "yes" == "$insecure" ];
    then
        command="${command} --insecure";
    fi;

    command="${command} ${apiurl}/post";

    if [ "yes" == "$verbose" ];
    then
        command="${command} -v";
        echo $command;
    fi;

    eval $command;
    echo;
}

