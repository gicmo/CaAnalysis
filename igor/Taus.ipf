#pragma rtGlobals=3		// Use modern global access method and strict wave access.

function taus(condition, ages)

string condition
string ages

//XLLoadWave/S="Sheet1"/R=(A1,C91)/W=1/D/T/V=0/K=0 "Macintosh HD:Users:delwen:Documents:Figures:Taus:Taus.xlsx"

makenameofcells("X*", condition)

string index = Wavelist("X*" +"*" + condition + "*",";","")
print index 

variable n,x,p,i,c,z,a
variable endpnt = 89
variable factor = 0.03

make/N=90 time_axis
make W_coef

for (p=0;p<numpnts(time_axis);p+=1)
	time_axis[p] = 0 + p*0.03
endfor

make/T/N=(itemsinlist(index)) database
wave/T database = $("database_" + condition)

wave/T nameofcell = $("nameofcell")

for (n=0;n<(numpnts(database));n+=1)
	database[n] = stringfromlist(n,index)
endfor

make/N=(itemsinlist(index)) peak
make/N=(itemsinlist(index)) peaktime
make/N=(itemsinlist(index)) baseline
make/N=(itemsinlist(index)) half_width
make/N=(itemsinlist(index)) delta_x
make/N=(itemsinlist(index)) delta_y
make/N=(itemsinlist(index)) half_width_pre
make/N=(itemsinlist(index)) Tau

strswitch (ages)
	case "control":
	make age_C = {10,11,13,14,15,16}
	break
	
	case "noisebox":
	make age_C = {14,15,16}
	break 
endswitch

wave W_coef = W_coef

for (x=0;x<numpnts(database);x+=1)
	
	string wta = database[x]
	Duplicate/O $wta, $(wta + "_smt_" + condition)
	Smooth/B 3, $(wta + "_smt_" + condition)
	wavestats/Q/R=(2,8) $(wta + "_smt_" + condition)
	baseline[x] = V_avg
	wavestats/Q $(wta + "_smt_" + condition)
	peak[x] = V_max - baseline[x]
	peaktime[x] = V_maxloc
	
	FindLevel/Q/R=(0,peaktime[x]) $(wta + "_smt_" + condition), (peak[x]/2)
	a = V_LevelX*factor
	FindLevel/Q/R=(peaktime[x],endpnt) $(wta + "_smt_" + condition), (peak[x]/2)
	half_width_pre[x] = (V_LevelX*factor) - a
	half_width[x] = half_width_pre[x]/peak[x]
	delta_x[x] = (V_LevelX*factor) - (peaktime[x]*factor)
	delta_y[x] = peak[x] - peak[x]/2
	Tau[x] = delta_y[x]/delta_x[x]
	
	
//	CurveFit/Q/NTHR=0 exp_XOffset  $(wta + "_smt_" + condition)(peaktime,endpnt) /D 
//	Tau[x] = W_coef[2]*factor

endfor

edit database, peak, half_width, Tau

make/N=1 hw_average_tmp
make/N=1 tau_average_tmp

make/N=0 hw_average
make/N=0 tau_average

for (i=0;i<numpnts(nameofcell);i+=1)
	wave T_hw = $("half_width")
	wave T_Tau = $("Tau")
	Extract /FREE/INDX database, tempwave, (Stringmatch(database, "*" + nameofcell[i] + "*") == 1)
	make/o/N=(numpnts(tempwave)) $(nameofcell[i] + "_hw_" + condition)
	make/o/N=(numpnts(tempwave)) $(nameofcell[i] + "_tau_" + condition)
	wave dest_hw = $(nameofcell[i] + "_hw_" + condition)
	wave dest_tau = $(nameofcell[i] + "_tau_" + condition)
	
	for (c=0;c<numpnts(tempwave);c+=1)
		dest_hw[c][] = T_hw[tempwave[c]]
		dest_Tau[c][] = T_Tau[tempwave[c]]	
	endfor
	
	wavestats/Q $(nameofcell[i] + "_hw_" + condition)
	hw_average_tmp = V_avg
	duplicate/o hw_average_tmp, $("AW_hw_" + nameofcell[i] + "_" + condition)

	wavestats/Q $(nameofcell[i] + "_tau_" + condition)
	tau_average_tmp = V_avg
	duplicate/o tau_average_tmp, $("AW_tau_" + nameofcell[i] + "_" + condition)
	
	variable pts = numpnts(hw_average)
	variable next = pts+1
	redimension/N=(next) hw_average
	hw_average[pts] = hw_average_tmp
	redimension/N=(next) tau_average
	tau_average[pts] = tau_average_tmp

	
endfor

make/N=(numpnts(age_C)) hw_per_age
make/N=(numpnts(age_C)) tau_per_age
make/N=(numpnts(age_C)) hw_med_per_age
make/N=(numpnts(age_C)) tau_med_per_age
make/N=(numpnts(age_C)) hw_Q1_per_age
make/N=(numpnts(age_C)) tau_Q1_per_age
make/N=(numpnts(age_C)) hw_Q3_per_age
make/N=(numpnts(age_C)) tau_Q3_per_age

for (z=0; z<numpnts(age_C);z+=1)
	Extract /FREE/INDX nameofcell, age_temp, (Stringmatch(nameofcell, "*_p" + num2str(age_C[z])) == 1)
	make/o/N=(numpnts(age_temp)) hw_all_temp
	make/o/N=(numpnts(age_temp)) tau_all_temp
	 wave hw_all_temp = $("hw_all_temp")
	 wave tau_all_temp = $("tau_all_temp")
	 
	 for (c=0;c<numpnts(age_temp);c+=1)
		hw_all_temp[c][] = hw_average[age_temp[c]]
		tau_all_temp[c][] = tau_average[age_temp[c]]
	endfor
	
	duplicate hw_all_temp, $("hw_all_temp_" + condition + "_" + num2str(age_C[z]))
	duplicate tau_all_temp, $("Tau_all_temp_" + condition + "_" + num2str(age_C[z]))
	
	wavestats/Q hw_all_temp
	hw_per_age[z] = V_avg
	statsquantiles hw_all_temp
	hw_med_per_age[z] = V_Median
	hw_Q1_per_age[z] = V_Median - V_Q25
	hw_Q3_per_age[z] = V_Q75 - V_Median
	
	wavestats/Q tau_all_temp
	tau_per_age[z] = V_avg
	statsquantiles tau_all_temp
	tau_med_per_age[z] = V_Median
	tau_Q1_per_age[z] = V_Median - V_Q25
	tau_Q3_per_age[z] = V_Q75 - V_Median

endfor	
	
edit age_C, hw_per_age, tau_per_age

//----------------------------------------------------------------------------------- plotting function

Display hw_per_age vs age_C
ModifyGraph mode=3,marker=8,msize=3.5,mrkThick=1,rgb=(0,0,0)
SetAxis bottom 9,16
SetAxis left 0,1
AppendToGraph/R tau_per_age vs age_C
SetAxis right 0,1.5
ModifyGraph mode=3,msize=3.5,mrkThick=1,rgb=(0,0,0),marker(tau_per_age)=19
ModifyGraph nticks(left)=2,nticks(right)=2
ModifyGraph fSize=11,axThick=1.2
ModifyGraph btLen=3
ErrorBars hw_per_age Y,wave=(hw_Q1_per_age, hw_Q3_per_age)
ErrorBars tau_per_age Y,wave=(tau_Q1_per_age, tau_Q3_per_age)
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






