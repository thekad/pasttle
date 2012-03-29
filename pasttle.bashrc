#!/bin/bash

function pasttle(){
#   default values
    encrypt="yes";
    filename="-";
    verbose="no";
    insecure="no";

#   load user preferences
    if [ -f "~/.pasttlerc" ];
    then
        source ~/.pasttlerc;
    fi;

#   load runtime options
    OPTIND=1;
    while getopts ":a:np:f:vi" flag;
    do
        case $flag in
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

    command="curl -F 'upload=@${filename}'"

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
        echo $command;
    fi;

    eval $command;
    echo;
}

