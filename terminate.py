

step1 = '''Thank you for inquiring about the Energy Savings Assistance Program.  Your utility company has contracted with another company to service homes in your area.  You can visit your utility company's website to find a an authorized contractor in your area. 

<a href="http://www.pge.com/en/myhome/saveenergymoney/financialassistance/energysavingsassistanceprogram/index.page">PG&E</a>

<a href="https://www.sce.com/wps/portal/home/residential/assistance/energy-saving-program/!ut/p/b1/hc_NCoJAFAXgZ2nhMufoRFm7kdRGIimjbDahYaNgTpglvX0WbaK_uzuX78C9RJCIiDK-5DKuc1XGxT2L_tawPDbhIbhlUwfcRjBjCwbPGbRg0wJ8GYZ__TURr8RzjTG4vzLCKcbouXgDi4F5B840sA0TlvkEQw_OxA9asJxTcDrHLGSMAv0n-HGkT4QsVPJ4eMPKhFqSiCrdp1Va6eeqXWd1fTyNNGhomkaXSski1XfqoOFTJVOnmkSvkhwPEXLeFcm16dwACNTqCA!!/dl4/d5/L2dBISEvZ0FBIS9nQSEh/?from=esap">SCE</a>

<a href="http://www.socalgas.com/for-your-home/assistance-programs/esap/">SoCal Gas</a>

<a href="http://www.sdge.com/energy-savings-assistance-program">SD G&E </a>

Thank you again for the inquiry.  If you have any friends or family in Stanislaus, San Joaquin, Fresno, Kings, Tulare and Kern county please let them know and we can help them directly!'''

step3 = '''

Thank you for inquiring about the Energy Savings Assistance Program.  

At this time, you do not meet the income requires for this program.  These guidelines are updated every year in June.  Please try again then.

For more information about this program you can visit PG&E and/or SoCal Gas's website below:

<a href="http://www.pge.com/en/myhome/saveenergymoney/financialassistance/energysavingsassistanceprogram/index.page">PG&E</a>

<a href="http://www.socalgas.com/for-your-home/assistance-programs/esap/">SoCal Gas</a>

Thank you again for the inquiry.  If you have any friends or family in Stanislaus, San Joaquin, Fresno, Kings, Tulare and Kern county please let them know and we can help them directly!'''

step4 = '''Thank you for inquiring about the Energy Savings Assistance Program.  

The age of the home is verfied during the enrollment process and must be at least 5 years old at the time of enrollment.  

For more information about this program you can visit PG&E and/or SoCal Gas's website below:
<a href="http://www.pge.com/en/myhome/saveenergymoney/financialassistance/energysavingsassistanceprogram/index.page">PG&E</a>

<a href="http://www.socalgas.com/for-your-home/assistance-programs/esap/">SoCal Gas</a>

Thank you again for the inquiry.  If you have any friends or family in Stanislaus, San Joaquin, Fresno, Kings, Tulare and Kern county please let them know and we can help them directly!'''

step5 = ''' '''

msg = {'previously_enrolled' : '''Thank you for inquiring about the Energy Savings Assistance Program.  

This address matched an existing inquiry in our database.

Unfortunately, your property has been previously serviced in this program and cannot be serviced again at this time.  The service may have occurred prior to your occupancy in the home.  

The guidelines change every year in June, please check back to see if your home qualfies then.

If you require more information you may reply or simply visit your electric and gas companies website:

Thank you for your interest. We hope you will share this information with your friends family and neighbors that could use these free repairs, upgrades and discounts.

''',

 'appointment_set' : ''' An appointment for the Energy Specialist is set for [date] at [time].  No further action is necessary at this time.  

If you require further assistance you can call 559-320-1313 between the hours of 9am and 6pm Monday through Friday.

Thank you.
''',

'awaiting_utility_response' : ''' We have received your application and have sent the request to your gas company.

We will contact you as soon as they follow up with us.

Thank you.
 ''',
 'closed' : ''' We have received your application and have been unable to contact you by phone.  Please check below to see if your contact information is correct.

[Record Details] (ability for applicant to edit)
''',
'utility_authorization_needed' : ''' We have received your application and have sent the request to your Property Mangager / Landlord.

We will contact you as soon as they follow up with us.

Thank you.
''',
'new' : ''' We have received your application and will contact you shortly.

No further action is necessary.

Thank you.
''',
'owner_refused' : ''' Our records indicate that your landlord refused the program.  

You met the qualfications but this program requires authorization from landlords, owners or property managers for all renters.

We will ocntact you in the future if your landlord provides us with authorization.

In the mean time, If you have any friends or family in Stanislaus, San Joaquin, Fresno, Kings, Tulare and Kern county please let them know and we can help them directly! "
 ''',
 'customer_refused' : ''' Our records indicate that the person we contacted refused this program.  

You are qualfied to ttake advantage of this free program.   Would you like tohave someone enroll you into this program now?
''',

'default' : '''  "We have received your application and will contact you shortly.

No further action is necessary.

Thank you.
" '''


}




def terminate(status):
	if status in msg.keys():
		return msg[status]
	return msg['default']

