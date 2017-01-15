#pragma rtGlobals=3		// Use modern global access method and strict wave access.

function profile()

XLLoadWave/S="Sheet1"/R=(B1,B228)/W=1/D/T/V=0/K=0 "Macintosh HD:Users:delwen:Documents:Profile_d_length.xlsx"
XLLoadWave/S="Sheet1"/R=(A1,A67)/COLT="T"/W=1/D/T/V=0/K=0 "Macintosh HD:Users:delwen:exclude.xlsx"						


// first I want to make a table with the wave names

variable x,n,j,w,a,b,f

string index = Wavelist("X*",";","")

wave D_length = $("D_length")
duplicate D_length, D_length_all

make/T/N=(itemsinlist(index)) cellname
make/T/N=(itemsinlist(index)) allcellname

for (a=0;a<numpnts(cellname);a+=1)
	cellname[a] = stringfromlist(a, index)
	allcellname[a] = stringfromlist(a,index)
endfor

printf "# cells before exclude: %d\r", numpnts(cellname)
 
string ind_list = wavelist("cellname", ";", "")
wave/T id=$(stringfromlist(0, ind_list))


// create exclude list and remove the cells that are on the exclude list

wave/T exclude = $("exclude")

variable i
for (i=0;i<numpnts(exclude); i += 1) 
	string to_exclude = exclude[i]
	Extract /FREE/INDX cellname, idx, (StringMatch(cellname[p], to_exclude) == 1)
	if (numpnts(idx) < 1)
	      printf "[%s] NOT FOUND\r", to_exclude
	      continue
	endif
	DeletePoints idx[0], 1, cellname
	DeletePoints idx[0], 1, D_length
endfor

// then I want to go through the list of waves and perform wavestats and store Vmax and Vmaxloc values

variable n_cells = numpnts(cellname)
printf "# cells after exclude: %d\r", n_cells

make/N=(n_cells) max_dFF
make/N=(n_cells) tmax_dFF


edit cellname
appendtotable D_length

variable k
for (k=0; k<n_cells; k+=1)
	SetScale/P x 0,0.4933,"um",$cellname[k]
	Duplicate/O $cellname[k], $(cellname[k] + "smth")
	Smooth/B 3, $(cellname[k] + "smth")
	wavestats/Q $(cellname[k] + "smth")
	max_dFF[k] = V_max
	tmax_dFF[k] = V_maxloc
	appendtotable max_dFF
	appendtotable tmax_dFF
	KillWaves $cellname[k] + "smth"
endfor

//here I still need to apply the exlude table to the length values!!!


// plot the median values of V_maxloc vs the age

make age_C = {10,11,13,14,15,16,17,18}
make age_NB = {14,15,16,17,18}
wave age_C
wave age_NB

make/N=(numpnts(age_C)) Median_C
make/N=(numpnts(age_C)) Median_length_C
make/N=(numpnts(age_C)) Median_length_all_C
make/N=(numpnts(age_NB)) Median_NB
make/N=(numpnts(age_NB)) Median_length_NB
make/N=(numpnts(age_NB)) Median_length_all_NB
wave Median_C
wave Median_length_C
wave Median_length_NB
wave Median_length_all_C
wave Median_length_all_NB
wave Median_NB
make/N=(numpnts(age_C)) Q1_C
make/N=(numpnts(age_C)) Q1_length_C
make/N=(numpnts(age_C)) Q1_length_all_C
make/N=(numpnts(age_NB)) Q1_NB
make/N=(numpnts(age_NB)) Q1_length_NB
make/N=(numpnts(age_NB)) Q1_length_all_NB

wave Q1_C
wave Q1_length_C
wave Q1_length_NB
wave Q1_length_all_C
wave Q1_length_all_NB
wave Q1_NB
make/N=(numpnts(age_C)) Q3_C
make/N=(numpnts(age_C)) Q3_length_C
make/N=(numpnts(age_C)) Q3_length_all_C
make/N=(numpnts(age_NB)) Q3_NB
make/N=(numpnts(age_NB)) Q3_length_NB
make/N=(numpnts(age_NB)) Q3_length_all_NB
wave Q3_C
wave Q3_length_C
wave Q3_length_NB
wave Q3_length_all_C
wave Q3_length_all_NB
wave Q3_NB

variable c,d,g,h,o,m,e,q,t


// create wave containing all the tmax_dFF values for an age group

string list = wavelist("cellname", ";", "")
wave/T wt=$(stringfromlist(0, list))

for (c=0; c<numpnts(age_C);c+=1)
      wave tdff=$("tmax_dFF")
	Extract /FREE/INDX cellname, tempwave, (StringMatch(cellname[p], "*p" + num2str(age_C[c]) + "_control*") == 1)
	make/o/N=(numpnts(tempwave))  $("tmax_dFF_control_" + num2str(age_C[c])) = NaN
	wave dest = $("tmax_dFF_control_" + num2str(age_C[c]))
	
	for (x=0;x<numpnts(tempwave);x+=1)
		dest[x][] = tdff[tempwave[x]]
	endfor
	
endfor
	
	
for (d=0; d<numpnts(age_NB);d+=1)
      wave tdff=$("tmax_dFF")
	Extract /FREE/INDX cellname, newwave, (StringMatch(cellname[p], "*p" + num2str(age_NB[d]) + "_noisebox*") == 1)
	make/o/N=(numpnts(newwave))  $("tmax_dFF_NB_" + num2str(age_NB[d])) = NaN
	wave dest_NB = $("tmax_dFF_NB_" + num2str(age_NB[d]))
	
	for (o=0;o<numpnts(newwave);o+=1)
		dest_NB[o][] = tdff[newwave[o]]
	endfor
	
endfor


for (e=0;e<numpnts(age_C);e+=1)
      wave tlength=$("D_length")
	Extract /FREE/INDX cellname, otherwave, (StringMatch(cellname[p], "*p" + num2str(age_C[e]) + "_control*") == 1)
	make/o/N=(numpnts(otherwave))  $("D_length_control_" + num2str(age_C[e])) = NaN
	wave length_dest = $("D_length_control_" + num2str(age_C[e]))
	
	for (m=0;m<numpnts(otherwave);m+=1)
		length_dest[m][] = tlength[otherwave[m]]
	endfor
	
endfor

for (q=0;q<numpnts(age_NB);q+=1)
      wave tlength=$("D_length")
	Extract /FREE/INDX cellname, newotherwave, (StringMatch(cellname[p], "*p" + num2str(age_NB[q]) + "_noisebox*") == 1)
	make/o/N=(numpnts(newotherwave))  $("D_length_noisebox_" + num2str(age_NB[q])) = NaN
	wave length_dest_NB = $("D_length_noisebox_" + num2str(age_NB[q]))
	
	for (t=0;t<numpnts(newotherwave);t+=1)
		length_dest_NB[t][] = tlength[newotherwave[t]]
	endfor
	
endfor


//-------------------------------------------------------------------------------

variable s, u, l, r

for (u=0;u<numpnts(age_C);u+=1)
      wave tlengthC=$("D_length_all")
	Extract /FREE/INDX allcellname, allwavesC, (StringMatch(allcellname[p], "*p" + num2str(age_C[u]) + "_control*") == 1)
	make/o/N=(numpnts(allwavesC))  $("D_length_control_all_" + num2str(age_C[u])) = NaN
	wave length_dest_all_C = $("D_length_control_all_" + num2str(age_C[u]))
	
	for (s=0;s<numpnts(allwavesC);s+=1)
		length_dest_all_C[s][] = tlengthC[allwavesC[s]]
	endfor
	
endfor

for (l=0;l<numpnts(age_NB);l+=1)
      wave tlengthNB=$("D_length_all")
	Extract /FREE/INDX allcellname, allwavesNB, (StringMatch(allcellname[p], "*p" + num2str(age_NB[l]) + "_noisebox*") == 1)
	make/o/N=(numpnts(allwavesNB))  $("D_length_noisebox_all_" + num2str(age_NB[l])) = NaN
	wave length_dest_all_NB = $("D_length_noisebox_all_" + num2str(age_NB[l]))
	
	for (r=0;r<numpnts(allwavesNB);r+=1)
		length_dest_all_NB[r][] = tlengthNB[allwavesNB[r]]
	endfor
	
endfor


// calculate the median, Q1, and Q3 values for each age group and put them in a main table

for(c=0; c<numpnts(age_C);c+=1)
	
	statsquantiles/Q $("tmax_dFF_control_" + num2str(age_C[c]))
	Median_C[c] = V_median
	Q1_C[c] = V_Median - V_Q25
	Q3_C[c] = V_Q75 - V_Median
	statsquantiles/Q $("D_length_control_" + num2str(age_C[c]))
	Median_length_C[c] = V_median
	Q1_length_C[c] = V_Median - V_Q25
	Q3_length_C[c] = V_Q75 - V_Median
	statsquantiles/Q $("D_length_control_all_" + num2str(age_C[c]))
	Median_length_all_C[c] = V_median
	Q1_length_all_C[c] = V_Median - V_Q25
	Q3_length_all_C[c] = V_Q75 - V_Median
	
endfor

	
for (d=0; d<numpnts(age_NB);d+=1)

	statsquantiles/Q $("D_length_noisebox_all_" + num2str(age_NB[d]))
	Median_length_all_NB[d] = V_median
	Q1_length_all_NB[d] = V_Median - V_Q25
	Q3_length_all_NB[d] = V_Q75 - V_Median
	
	if (numpnts($("tmax_dFF_NB_" + num2str(age_NB[d]))) < 3)
		print "median not possible for tmax_dFF_NB_" + num2str(age_NB[d])
		wavestats Median_NB 
		Median_NB[d] = V_avg
		wavestats Median_length_NB
		Median_length_NB[d] = V_avg
		
		//Median_NB[d] = NaN
		//Median_length_NB[d] = NaN
		
		continue
	endif
	
	statsquantiles/Q $("tmax_dFF_NB_" + num2str(age_NB[d]))
	Median_NB[d] = V_median
	Q1_NB[d] = V_Median - V_Q25
	Q3_NB[d] = V_Q75 - V_Median
	statsquantiles/Q $("D_length_noisebox_" + num2str(age_NB[d]))
	Median_length_NB[d] = V_median
	Q1_length_NB[d] = V_Median - V_Q25
	Q3_length_NB[d] = V_Q75 - V_Median


endfor

//------------------------------------------------------------------------------- plotting functions

// display control graph + NB graph

display Median_C vs age_C
Appendtograph Median_NB vs age_NB
ErrorBars Median_C Y, wave=(Q3_C,Q1_C)
ErrorBars Median_NB Y, wave=(Q3_NB,Q1_NB)
ModifyGraph mode(Median_C)=3,marker(Median_C)=19,rgb(Median_C)=(0,0,0)
ModifyGraph mode(Median_NB)=3,marker(Median_NB)=19, rgb(Median_NB)=(65535,43690,0)
ModifyGraph mode(Median_C)=4,lstyle(Median_C)=2
ModifyGraph mode(Median_NB)=4,lstyle(Median_NB)=2
ModifyGraph msize=3.5,mrkThick=1
ModifyGraph fSize=11,axThick=1.2
ModifyGraph nticks(left)=3
SetAxis left 0,200
SetAxis bottom 9,20
ModifyGraph nticks=3
Label left "\\Z12Dendritic location (pix)"
Label bottom "\\Z12Postnatal day (P)"

// display control graph only

display Median_C vs age_C
Appendtograph/R Median_length_C vs age_C
ErrorBars Median_C Y, wave=(Q3_C,Q1_C)
ErrorBars Median_length_C Y, wave=(Q3_length_C,Q1_length_C)
ModifyGraph mode=3,marker=19,rgb=(0,0,0)
ModifyGraph mode(Median_length_C)=3,marker(Median_length_C)=8,rgb(Median_length_C)=(0,0,0)
ModifyGraph mode(Median_C)=4,lstyle(Median_C)=2
ModifyGraph msize=3.5,mrkThick=1
ModifyGraph fSize=11,axThick=1.2
ModifyGraph nticks(left)=3
SetAxis right 0,100
SetAxis left 0,200
SetAxis bottom 9,20
ModifyGraph nticks=3
Label right "\\Z12Dendrite length (um)"
Label left "\\Z12Dendritic location (pix)"
Label bottom "\\Z12Postnatal day (P)"

// display control graph only with all dendritic lengths

display Median_C vs age_C
Appendtograph/R Median_length_all_C vs age_C
ErrorBars Median_C Y, wave=(Q3_C,Q1_C)
ErrorBars Median_length_all_C Y, wave=(Q3_length_all_C,Q1_length_all_C)
ModifyGraph mode=3,marker=19,rgb=(0,0,0)
ModifyGraph mode(Median_length_all_C)=3,marker(Median_length_all_C)=8,rgb(Median_length_all_C)=(0,0,0)
ModifyGraph mode(Median_C)=4,lstyle(Median_C)=2
ModifyGraph msize=3.5,mrkThick=1
ModifyGraph fSize=11,axThick=1.2
ModifyGraph nticks(left)=3
SetAxis right 0,100
SetAxis left 0,200
SetAxis bottom 9,20
ModifyGraph nticks=3
Label right "\\Z12Dendrite length (um)"
Label left "\\Z12Dendritic location (pix)"
Label bottom "\\Z12Postnatal day (P)"

// display noisebox graph

display Median_NB vs age_NB
Appendtograph/R Median_length_NB vs age_NB
ErrorBars Median_NB Y, wave=(Q3_NB,Q1_NB)
ErrorBars Median_length_NB Y, wave=(Q3_length_NB,Q1_length_NB)
ModifyGraph mode(Median_NB)=3,marker(Median_NB)=19,rgb(Median_NB)=(65535,43690,0)
ModifyGraph mode(Median_length_NB)=3,marker(Median_length_NB)=8,rgb(Median_length_NB)=(65535,43690,0)
ModifyGraph mode(Median_NB)=4,lstyle(Median_NB)=2
ModifyGraph msize=3.5,mrkThick=1
ModifyGraph fSize=11,axThick=1.2
ModifyGraph nticks(left)=3
SetAxis right 0,100
SetAxis left 0,200
SetAxis bottom 9,20
ModifyGraph nticks=3
Label right "\\Z12Dendrite length (um)"
Label left "\\Z12Dendritic location (pix)"
Label bottom "\\Z12Postnatal day (P)"


// display noisebox graph with all dendritic lengths

display Median_NB vs age_NB
Appendtograph/R Median_length_all_NB vs age_NB
ErrorBars Median_NB Y, wave=(Q3_NB,Q1_NB)
ErrorBars Median_length_all_NB Y, wave=(Q3_length_all_NB,Q1_length_all_NB)
ModifyGraph mode(Median_NB)=3,marker(Median_NB)=19,rgb(Median_NB)=(65535,43690,0)
ModifyGraph mode(Median_length_all_NB)=3,marker(Median_length_all_NB)=8,rgb(Median_length_all_NB)=(65535,43690,0)
ModifyGraph mode(Median_NB)=4,lstyle(Median_NB)=2
ModifyGraph msize=3.5,mrkThick=1
ModifyGraph fSize=11,axThick=1.2
ModifyGraph nticks(left)=3
SetAxis right 0,100
SetAxis left 0,200
SetAxis bottom 9,20
ModifyGraph nticks=3
Label right "\\Z12Dendrite length (um)"
Label left "\\Z12Dendritic location (pix)"
Label bottom "\\Z12Postnatal day (P)"

//edit Median_C, Q1_C, Q3_C
//edit Median_NB, Q1_NB, Q3_NB

end