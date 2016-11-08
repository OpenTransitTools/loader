RUN STRESS TESTS 



general url path of /prod, iterating one time over the 'regression' suite, with a single thread:

* http://maps7:80/prod?submit&module=planner&fromPlace=ME::45.468019,-122.655552&toPlace=OHSU::45.499049,-122.684283
* bin/otp_stress_test  -ts regres -n 1 -t 1 -hn maps7 -ws /prod none # test url
* bin/otp_stress_test -n  1 -t 10 -hn maps8 -ws /prod none  # moderate load 
* bin/otp_stress_test -n 30 -t 20 -hn maps8 -ws /prod none  # large load (will take many hours)
* bin/otp_stress_test -n 50 -t 50 -hn maps8 -ws /prod none  # huge load over time (may never finish)


test the ride service and ride html rendering:

http://dev.trimet.org/#planner/results/from=pdx&to=zoo

http://maps8/ride/ws/planner_form.html

* bin/otp_stress_test -ts regres -s plan.*itineraries -n 1 -t 1 -hn maps8 -ws /ride_ws/plan_trip none # test ride_ws
* bin/otp_stress_test -ts regres -s itinerary.*step-number.*directions -np -n 1 -t 1 -hn maps8 -ws /ride/ws/planner.html none # test view html page 


## generate a file of urls for trimet.org
* bin/otp_stress_test -ts regres -np -strip ?submit\&module=planner\& -hn dev -ws /#planner/results/ none 

