python3 ttb_scraper.py
echo 'finished scraping ttb'

python3 calendar_scraper.py
echo 'finished scraping calendar'

python3 merge_course_lists.py > ./Data/unmergeable_courses.txt
echo 'finished merging courses'

python3 earlist_takeable.py
echo 'finished generating earliest takeable date'