#pragma rtGlobals=3		// Use modern global access method and strict wave access.

function taus()

//XLLoadWave/S="Sheet1"/R=(A1,C91)/W=1/D/T/V=0/K=0 "Macintosh HD:Users:delwen:Documents:Figures:Taus:Taus.xlsx"

makenameofcells("X*")

string index = Wavelist("X*",";","")
print index 

variable n,x,a,p,i,c,s,t,b,d,q,z,w,k
variable endpnt = 89
variable factor = 0.03

make/N=90 time_axis
make W_coef

for (p=0;p<numpnts(time_axis);p+=1)
	time_axis[p] = 0 + p*0.03
endfor

make/T/N=(itemsinlist(index)) database

wave/T nameofcell = $("nameofcell")

for (n=0;n<(numpnts(database));n+=1)
	database[n] = stringfromlist(n,index)
endfor

make/N=(itemsinlist(index)) peak
make/N=(itemsinlist(index)) peaktime
make/N=(itemsinlist(index)) baseline
make/N=(itemsinlist(index)) half_width
make/N=(itemsinlist(index)) Tau

make age_C = {10,13}

wave W_coef = W_coef

for (x=0;x<numpnts(database);x+=1)
	
	string wta = database[x]
	Duplicate/O $wta, $(wta + "_smth")
	Smooth/B 3, $(wta + "_smth")
	wavestats/Q/R=(2,8) $(wta + "_smth")
	baseline[x] = V_avg
	wavestats/Q $(wta + "_smth")
	peak[x] = V_max - baseline[x]
	peaktime[x] = V_maxloc
	
	FindLevel/Q/R=(0,peaktime[x]) $(wta + "_smth"), (peak[x]/2)
	a = V_LevelX*factor
	FindLevel/Q/R=(peaktime[x],endpnt) $(wta + "_smth"), (peak[x]/2)
	half_width[x] = (V_LevelX*factor) - a
	
	CurveFit/NTHR=0 exp_XOffset  $(wta + "_smth")(peaktime,endpnt) /D 
	Tau[x] = W_coef[2]*factor

endfor

edit database, peak, half_width, Tau

make/N=1 hw_average_tmp
make/N=1 tau_average_tmp

make/N=0 hw_average
make/N=0 tau_average

for (i=0;i<numpnts(nameofcell);i+=1)
	wave T_hw = $("half_width")
	wave T_Tau = $("Tau")
	Extract /FREE/INDX database, tempwave, (Stringmatch(database, nameofcell[i] + "*") == 1)
	make/o/N=(numpnts(tempwave)) $(nameofcell[i] + "_hw")
	make/o/N=(numpnts(tempwave)) $(nameofcell[i] + "_tau")
	wave dest_hw = $(nameofcell[i] + "_hw")
	wave dest_tau = $(nameofcell[i] + "_tau")
	
	for (c=0;c<numpnts(tempwave);c+=1)
		dest_hw[c][] = T_hw[tempwave[c]]
		dest_Tau[c][] = T_Tau[tempwave[c]]	
	endfor
	
	wavestats $(nameofcell[i] + "_hw")
	hw_average_tmp = V_avg
	duplicate/o hw_average_tmp, $("AW_hw_" + nameofcell[i])

	wavestats $(nameofcell[i] + "_tau")
	tau_average_tmp = V_avg
	duplicate/o tau_average_tmp, $("AW_tau_" + nameofcell[i])
	
	variable pts = numpnts(hw_average)
	variable next = pts+1
	redimension/N=(next) hw_average
	hw_average[pts] = hw_average_tmp
	
endfor

make/N=(numpnts(age_C)) hw_per_age
for (z=0; z<numpnts(age_C);z+=1)
	Extract /FREE/INDX nameofcell, age_temp, (Stringmatch(nameofcell, "*_p" + num2str(age_C[z])) == 1)
	make/o/N=(numpnts(age_temp)) hw_all_temp
	 wave hw_all_temp = $("hw_all_temp")
	 
	 for (c=0;c<numpnts(age_temp);c+=1)
		hw_all_temp[c][] = hw_average[age_temp[c]]
		//tau_all_temp[c][] =...
	endfor
	
	wavestats hw_all_temp
	hw_per_age[z] = V_avg
endfor	
	

end


function makenameofcells(pattern)
String pattern

string index = Wavelist(pattern,";","")

variable n,x,a,p,i,c,s,t,b,d,q,z,w,k

make/T/N=0 nameofcell
for (p=0;p<itemsinlist(index);p+=1)
	String regExp = "X([[:digit:]]{8,8}[[:alpha:]]{1,1})_p([[:digit:]]{2,2})_([[:digit:]]{0,2})$"
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

function foobar(condition)
String condition
print condition
end