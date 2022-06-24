#!/bin/bash

SW_VERSION="0.7"
UPSTREAM_URL="https://raw.github.com/thekad/pasttle/main/pasttle.bashrc"

function gettle() {
#   default values
    local encrypt="yes";
    local filename="-";
    local verbose="no";
    local insecure="no";
    local checkupdate="yes";
    local clipboard="no";
    local clipin="";
    local clipargs="";
    local command="";
    local password="";
    local upstream_version="$SW_VERSION";
#   You can override this via environment variable
    local rcfile=${PASTTLERC:-~/.pasttlerc}

    version="gettle/${SW_VERSION}/curl/$( curl --version | head -1 | cut -d\  -f2- )";
#   load user preferences
    if [ -f $rcfile ];
    then
        echo "Loading ${rcfile}" > /dev/stderr
        source $rcfile;
    fi;

    local usage="\n
    USAGE\n\n
    gettle [options] -e <entry number>\n\n
    OPTIONS\n\n
        -a  API URL, this is, the root URL of the service (var: apiurl)\n\n
        -n  Do not encrypt your password before sending it (var: encrypt)\n\n
        -p 'PASSWORD' If the entry is password-protected (var: password)\n\n
        -f 'FILENAME' (OPTIONAL) Output the content to the given file (ver: filename)\n\n
        -i (OPTIONAL) If you want to skip on SSL errors (var: insecure)\n\n
        -v (OPTIONAL) Print verbose output (var: verbose)\n\n
        -C (OPTIONAL) Don't check for updates from upstream (var: checkupdate)\n\n
        -x (OPTIONAL) Put contents in clipboard, requires xclip in linux (var: clipboard)\n\n
    "

#   load runtime options
    OPTIND=1;
    while getopts ":a:np:f:hviCxe:" flag;
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
            C)
                checkupdate="no"
                ;;
            x)
                clipboard="yes"
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

    if [ "yes" == "$checkupdate" ];
    then
        upstream_version="$(curl -s $UPSTREAM_URL | grep "^SW_VERSION" | cut -d\" -f2)";
        diff <(echo "$SW_VERSION") <(echo "$upstream_version" ) > /dev/null ||
        echo "The upstream version ($upstream_version from $UPSTREAM_URL) differs from your version ($SW_VERSION). Time to update?"
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

    if [ "yes" == "$clipboard" ];
    then
        case "$( uname -s )" in
            Linux)
                clipin="xclip";
                clipargs="-in -selection clipboard"
                ;;
            Darwin)
                clipin="pbcopy";
                ;;
        esac;
        if which $clipin &> /dev/null;
        then
            command="${command} | tee >(${clipin} ${clipargs})";
        fi;
    fi;

    eval $command;
    echo;
}

function pasttle() {
#   default values
    local encrypt="yes";
    local filename="-";
    local verbose="no";
    local insecure="no";
    local checkupdate="yes";
    local clipboard="no";
    local clipin="";
    local clipargs="";
    local command="";
    local syntax=""
    local password="";
    local upstream_version="$SW_VERSION";
#   You can override this via environment variable
    local rcfile=${PASTTLERC:-~/.pasttlerc}

    version="pasttle/${SW_VERSION}/curl/$( curl --version | head -1 | cut -d\  -f2- )";
#   load user preferences
    if [ -f $rcfile ];
    then
        echo "Loading ${rcfile}" > /dev/stderr
        source $rcfile;
    fi;

    local usage="\n
    USAGE\n\n
    cat 'filename.ext' | pasttle [options]\n\n
    or\n\n
    pasttle -f 'filename.ext' [options]\n\n
    OPTIONS\n\n
        -a  API URL, this is, the root URL of the service (var: apiurl)\n\n
        -n  Do not encrypt your password before sending it (var: encrypt)\n\n
        -p 'PASSWORD' If you want to protect this entry with a password (var: password)\n\n
        -f 'FILENAME' (OPTIONAL) Upload the given plain-text file (var: filename)\n\n
        -i (OPTIONAL) If you want to skip on SSL errors (var: insecure)\n\n
        -v (OPTIONAL) Print verbose output (var: verbose)\n\n
        -s (OPTIONAL) Force the syntax of the paste (var: syntax)\n\n
        -C (OPTIONAL) Don't check for updates from upstream (var: checkupdate)\n\n
        -x (OPTIONAL) Put resulting URL in clipboard, requires xclip in linux (var: clipboard)\n\n
    "

#   load runtime options
    OPTIND=1;
    while getopts ":a:s:np:f:hvCix" flag;
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
            x)
                clipboard="yes"
                ;;
            C)
                checkupdate="no"
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

    if [ "yes" == "$checkupdate" ];
    then
        upstream_version="$(curl -s $UPSTREAM_URL | grep "^SW_VERSION" | cut -d\" -f2)";
        diff <(echo "$SW_VERSION") <(echo "$upstream_version" ) > /dev/null ||
        echo "The upstream version ($upstream_version from $UPSTREAM_URL) differs from your version ($SW_VERSION). Time to update?"
    fi;

    if [ -z "$syntax" ];
    then
        syntax="${filename#*.}"
        if [ "yes" == "$verbose" ];
        then
            echo "Syntax is ${syntax}";
        fi;
    fi;

    command="curl -s -A '${version}' -F 'upload=<${filename}' -F 'filename=${filename}' -F 'syntax=${syntax}'"

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
    fi;

    if [ "yes" == "$clipboard" ];
    then
        case "$( uname -s )" in
            Linux)
                clipin="xclip";
                clipargs="-in -selection clipboard"
                ;;
            Darwin)
                clipin="pbcopy";
                ;;
        esac;
        if which $clipin &> /dev/null;
        then
            command="${command} | tee >(${clipin} ${clipargs})";
        fi;
    fi;

    if [ "yes" == "$verbose" ];
    then
        echo $command;
    fi;

    eval $command;

    echo;
}
