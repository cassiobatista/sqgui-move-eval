#!/bin/bash
#
# author: feb 2019
# cassio batista - cassio.batista.13@gmail.com
# http://www.imagemagick.org/Usage/compose/#math_blending

rm -f *.png
for d in dia/*.dia
do
	filename=$(echo $(basename $d) | sed 's/.dia//g')
	dia -t png -s 255x255 $d -e ./${filename}.png
done

# -----------------------------------------------------
mv halfline.png cr.png
cp cr.png lc.png

convert lc.png -rotate -180 cl.png
cp cl.png rc.png

convert rc.png -rotate -90 cd.png
cp cd.png uc.png

convert uc.png -rotate -180 cu.png
cp cu.png dc.png
# -----------------------------------------------------
composite cl.png lc.png -compose Multiply ll.png
cp ll.png rr.png

convert ll.png -rotate -90 uu.png
cp uu.png dd.png
# -----------------------------------------------------
composite rc.png uc.png -compose Multiply rd.png
cp rd.png ul.png

convert ul.png -rotate -180 lu.png
cp lu.png dr.png

convert dr.png -rotate -90 ru.png
cp ru.png dl.png

convert dl.png -rotate -180 ld.png
cp ld.png ur.png
# -----------------------------------------------------

function verify() {
	# check pairs
	convert cr.png lc.png +append out.png && eom out.png
	convert cl.png rc.png +append out.png && eom out.png
	convert cd.png uc.png +append out.png && eom out.png
	convert cu.png dc.png +append out.png && eom out.png
	
	convert ll.png rr.png +append out.png && eom out.png
	convert uu.png dd.png +append out.png && eom out.png
	
	convert rd.png ul.png +append out.png && eom out.png
	convert lu.png dr.png +append out.png && eom out.png
	convert ru.png dl.png +append out.png && eom out.png
	convert ld.png ur.png +append out.png && eom out.png
	
	rm out.png
}

#verify
