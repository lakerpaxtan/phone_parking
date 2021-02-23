# phone_parking

- Being addicted to your phone sucks
- This script donates to wikipedia if your phone isn't plugged in 
- Intended to be setup with a task scheduler (I run weekdays 1AM - 6AM hourly) 


# Details
- Only donates once per day (Honestly only did this to prevent task scheduler from running the script over and over on accident)
- Requires selenium with geckodriver (firefox) 
- Gets around auth issues by using cached profile information with firefox (kind of secure?) 
- Works with macOS, but haven't tested selenium side of things yet... probably need a different driver 
- Currently only works with iPhones 
- Made sure to have pretty great logging that's printed into a logging folder
