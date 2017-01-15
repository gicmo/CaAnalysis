#pragma rtGlobals=3		// Use modern global access method and strict wave access.

function profile(condition)

string condition

makenameofcells("X*", condition)

string index = Wavelist("X*" + condition + "*",";","")
print index 

variable n,x,p,i,c,z,a

make/T/N=(itemsinlist(index)) database
wave/T database = $("database_" + condition)

wave/T nameofcell = $("nameofcell")

for (n=0;n<(numpnts(database));n+=1)
	database[n] = stringfromlist(n,index)
endfor

make/N=(itemsinlist(index)) max_dFF
make/N=(itemsinlist(index)) tmax_dFF

strswitch (condition)
	case "CT":
	make age_C = {10,11,13,14,15,16,17,18}
	break
	
	case "NB":
	make age_C = {14,15,16,17,18}
	break 
endswitch

edit database

for (x=0;x<numpnts(database);x+=1)
	
	string wta = database[x]
	SetScale/P x 0,0.4933,"um",$wta
	Duplicate/O $wta, $(wta + "_smt_" + condition)
	Smooth/B 3, $(wta + "_smt_" + condition)
	wavestats/Q $(wta + "_smt_" + condition)
	max_dFF[x] = V_max
	tmax_dFF[x] = V_maxloc
	appendtotable max_dFF
	appendtotable tmax_dFF
	
endfor

edit database, max_dFF, tmax_dFF

make/N=1 tmaxdFF_average_tmp

make/N=0 tmaxdFF_average

for (i=0;i<numpnts(nameofcell);i+=1)
	wave tdff = $("tmax_dFF")
	Extract /FREE/INDX database, tempwave, (Stringmatch(database, "*" + nameofcell[i] + "*") == 1)
	make/o/N=(numpnts(tempwave)) $(nameofcell[i] + "_tmax_" + condition)
	wave dest_tmax = $(nameofcell[i] + "_tmax_" + condition)
	
	for (c=0;c<numpnts(tempwave);c+=1)
		dest_tmax[c][] = tdff[tempwave[c]]
	endfor
	
	wavestats $(nameofcell[i] + "_tmax_" + condition)
	tmaxdFF_average_tmp = V_avg
	duplicate/o tmaxdFF_average_tmp, $("AW_tmax_" + nameofcell[i] + "_" + condition)
	
	variable pts = numpnts(tmaxdFF_average)
	variable next = pts+1
	redimension/N=(next) tmaxdFF_average
	tmaxdFF_average[pts] = tmaxdFF_average_tmp

	
endfor

make/N=(numpnts(age_C)) tmax_per_age
make/N=(numpnts(age_C)) tmax_med_per_age
make/N=(numpnts(age_C)) tmax_Q1_per_age
make/N=(numpnts(age_C)) tmax_Q3_per_age

make/N=(numpnts(age_C)) dlen_per_age
make/N=(numpnts(age_C)) dlen_med_per_age
make/N=(numpnts(age_C)) dlen_Q1_per_age
make/N=(numpnts(age_C))dlen_Q3_per_age

for (z=0; z<numpnts(age_C);z+=1)
	Extract /FREE/INDX nameofcell, age_temp, (Stringmatch(nameofcell, "*_p" + num2str(age_C[z])) == 1)
	make/o/N=(numpnts(age_temp)) tmax_all_temp
	 wave tmax_all_temp = $("tmax_all_temp")
	 
	 for (c=0;c<numpnts(age_temp);c+=1)
		tmax_all_temp[c][] = tmaxdFF_average[age_temp[c]]
	endfor
	
	wavestats tmax_all_temp
	tmax_per_age[z] = V_avg
	statsquantiles tmax_all_temp
	tmax_med_per_age[z] = V_Median
	tmax_Q1_per_age[z] = V_Median - V_Q25
	tmax_Q3_per_age[z] = V_Q75 - V_Median

	string dl_index = Wavelist("X*_p" + num2str(age_C[z]) + "_" + condition + "_1",";","")
	make/o/N=(itemsinlist(dl_index)) dlen_temp
	for (x=0;x<itemsinlist(dl_index);x+=1)
		dlen_temp[x] = WaveLenNaNs(stringfromlist(x,dl_index))
	endfor
	wavestats/Q dlen_temp
	dlen_per_age[z] = V_avg
	statsquantiles dlen_temp
	dlen_med_per_age[z] = V_Median
	dlen_Q1_per_age[z] = V_Median - V_Q25
	dlen_Q3_per_age[z] = V_Q75 - V_Median
endfor	
	
edit age_C, tmax_per_age

//----------------------------------------------------------------------------------- plotting function

Display tmax_per_age vs age_C
ModifyGraph mode=3,marker=8,msize=3.5,mrkThick=1,rgb=(0,0,0)
SetAxis bottom 9,60
SetAxis left 0,200
ModifyGraph nticks(left)=2
ModifyGraph fSize=11,axThick=1.2
ModifyGraph btLen=3
ErrorBars tmax_per_age Y,wave=(tmax_Q1_per_age, tmax_Q3_per_age)
ModifyGraph nticks(bottom)=3

end


function makenameofcells(pattern, condition)
String condition
String pattern

string index = Wavelist(pattern,";","")

variable n,x,p,i,c,z,a

make/T/N=0 nameofcell
for (p=0;p<itemsinlist(index);p+=1)
	String regExp = "X([[:digit:]]{8,8}[[:alpha:]]{1,1})_p([[:digit:]]{2,2})_" + condition + "_([[:digit:]]{0,2})$"
	String cellname, age
	String bla = stringfromlist(p, index)
	SplitString /E=(regExp) bla, cellname, age
	if (!GrepString(bla, regExp))
	      print "Skipping " + bla
		continue
	endif
	
	String fullname =  cellname + "_p" + age
	Extract /FREE/INDX nameofcell, nametemp, (Stringmatch(nameofcell, fullname) == 1)
	if (numpnts(nametemp) < 1)
		print "adding " + fullname
		variable pts = numpnts(nameofcell)
		variable next = pts+1
		redimension/N=(next) nameofcell
		nameofcell[pts][] =  fullname
	endif
endfor

print nameofcell
end

function WaveLenNaNs(name)
String name
wave w = $(name)

variable np = numpnts(w)
variable i
variable n_nans = 0
for (i=0;i<np;i+=1)
if (numtype(w[i])==2)
  n_nans += 1
endif
endfor

variable dlen = np - n_nans
return dlen * 0.4933 
end




