import requests, csv
from bs4 import BeautifulSoup

### START CONFIG ###
target_url = 'http://inmate.kenoshajs.org/NewWorld.InmateInquiry/kenosha?Name=&SubjectNumber=&BookingNumber=&BookingFromDate=08%2F23%2F2020&BookingToDate=&Facility='
limit = None #3 # don't hit the site too hard when debugging; None for prod
protest_charges = ['FAIL TO COMPLY W/EMERGENCY MANAGEMENT ORDER OF STATE OR LOCAL GOVERNMENT']
outfile = open('all_kenosha_county_inmates_since_08232020.csv','w')
headers = ['name','subject_no','dob','gender','race','height','weight','address',\
        'booking_id','booking_date','release_date','prisoner_type','classification','housing',\
        'total_bond','total_bail','booking_origin','protest_charge?','charge_blob']
### END CONFIG ###

# collect urls from index page
target_content = requests.get(target_url).content

soup = BeautifulSoup(target_content,'html.parser')

inmates = [ 'http://inmate.kenoshajs.org' + x.get('href') for x in soup.find_all('a',attrs={'href':True}) if 'InmateInquiry' in x.get('href')][0:limit]

print(inmates)

inmate_rows = []

# get each inmate page
for inmate in inmates:
    inmate_content = requests.get(inmate).content
    inmate_soup = BeautifulSoup(inmate_content,'html.parser')
    
    # break down demos
    inmate_demo = inmate_soup.find('div',{'id':'DemographicInformation'}) 
    try:
        inmate_name = inmate_demo.find('li',{'class':'Name'}).find('span').get_text()
    except Exception, e:
        print([e, inmate])
        continue
    inmate_subjectno = inmate_demo.find('li',{'class':'SubjectNumber'}).find('span').get_text()
    inmate_dob = inmate_demo.find('li',{'class':'DateOfBirth'}).find('span').get_text()
    inmate_gender = inmate_demo.find('li',{'class':'Gender'}).find('span').get_text()
    inmate_race = inmate_demo.find('li',{'class':'Race'}).find('span').get_text()
    inmate_height = inmate_demo.find('li',{'class':'Height'}).find('span').get_text()
    inmate_weight = inmate_demo.find('li',{'class':'Weight'}).find('span').get_text()
    inmate_address = inmate_demo.find('li',{'class':'Address'}).find('span').get_text()


    # booking -- only the first one on the list!
    inmate_booking = inmate_soup.find_all('div',{'class':'Booking'})[0]
    booking_id = inmate_booking.find('h3').find('span').get_text()
    booking_date = inmate_booking.find('li',{'class':'BookingDate'}).find('span').get_text()
    release_date = inmate_booking.find('li',{'class':'ReleaseDate'}).find('span').get_text()
    prisoner_type = inmate_booking.find('li',{'class':'PrisonerType'}).find('span').get_text()
    classification = inmate_booking.find('li',{'class':'ClassificationLevel'}).find('span').get_text()
    housing = inmate_booking.find('li',{'class':'HousingFacility'}).find('span').get_text()
    total_bond = inmate_booking.find('li',{'class':'TotalBondAmount'}).find('span').get_text()
    total_bail = inmate_booking.find('li',{'class':'TotalBailAmount'}).find('span').get_text()
    booking_origin = inmate_booking.find('li',{'class':'BookingOrigin'}).find('span').get_text()

    charges_all = inmate_booking.find_all('td',{'class':'ChargeDescription'})
    # force charges_all to be a list for concatenation:
    charges_list = []
    for charge in charges_all:
        charges_list.append(charge.get_text())
    charges_blob = ' | '.join([x for x in charges_list])
    protest_charge_bool = False
    for charge in protest_charges:
        if charge in charges_blob:
            protest_charge_bool = True
    inmate_rows.append({
        'name': inmate_name,
        'subject_no': inmate_subjectno,
        'dob': inmate_dob,
        'gender': inmate_gender,
        'race': inmate_race,
        'height': inmate_height,
        'weight': inmate_weight,
        'address': inmate_address,
        'booking_id': booking_id,
        'booking_date': booking_date,
        'release_date': release_date,
        'prisoner_type': prisoner_type,
        'classification': classification,
        'housing': housing,
        'total_bond': total_bond,
        'total_bail': total_bail,
        'booking_origin': booking_origin,
        'protest_charge?': protest_charge_bool,
        'charge_blob': charges_blob})

# write out
outcsv = csv.DictWriter(outfile,headers)
outcsv.writeheader()

for row in inmate_rows:
    outcsv.writerow(row)

outfile.close()
