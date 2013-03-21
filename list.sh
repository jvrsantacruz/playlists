#!/bin/bash
# Javier Santacruz 04/06/2011

function help {
    echo "Usage: [options] playlist directory"
    echo "       -d Delete files in remote whether they are not in the playlist."
    echo "       -f Force coping files. Default behaviour is to skip already existing files."
    echo "       -l Hard link files instead of copying."
    echo "       -c Don't create remote dir if it doesn't exists."
    exit 2
}

# Parse options
delete=
force="--update"
link=
nocreate=
while getopts 'dflc' OPTION
do
	case ${OPTION} in
	    d) delete="--delete";;
            l) link="--link";;
            f) force="";;
	    c) nocreate=1;;
	    ?) help;;
	esac
done

shift $(($OPTIND - 1))

if [ $# -ne 2 ]; then
	printf "Error: Incorrect number of arguments.\n\n"
	help
fi

if [ ! -f $1 ]; then
	printf "Error: Playlist $1 doesn't exists.\n\n"
	help
fi

if [ ! -d $2 ] && [ -z $nocreate ]; then 
	mkdir $2

elif [ ! -d $2 ] && [ ! -z $nocreate ]; then
	printf "Error: Remote directory $2 doesn't exists.\n\n"
	help
fi

# Delete undesired files
if [ "$delete" ]; then
	# Remove files in remote which are not in the playlist.
	# Comm compares lists and gives two columns tab separated with files belonging only to one list.
	# Left column are elements which are in the first list but not in the second.
	# Sed removes second column, so we got files in $2 but not in $1
	comm -3 <(ls $2) <(grep -vZ '^#' $1 | xargs -i basename "{}" | sort) | sed -e "s/\t.*$//g" | xargs -i rm -v "$2/{}"
fi

# Process m3u playlist
BASE=$(dirname $1)
# force gives --update if is false avoiding copy when exists.
# link gives --link changing copy for linking
grep -vZ '^#' $1 | xargs -i cp $link $force --verbose "$BASE/{}" $2
