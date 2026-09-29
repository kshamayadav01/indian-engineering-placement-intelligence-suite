|Column Name                                   |Description
|--------------------------------------------  | ------------------------------------------- |
|Student_ID                                    |Unique identifier for each student record.   |
|Age                                           | Age of the student (18-25 years).           |
|Gender                                        |Gender of the student.                       |
|State                                         | Indian state associated with the student.   |
|Branch                                        |Engineering branch.                          |
|College_Tier                                  | Tier classification of the institution.     |
|CGPA                                          |Cumulative Grade Point Average (0-10).       |
|Attendance_Percentage                         | Student attendance percentage.              |
|DSA_Problems_Solved                           |Number of DSA problems solved.               |
|Aptitude_Score                                | Aptitude assessment score (0-100).          |
|Communication_Score                           |Communication assessment score (0-100).      |
|Projects_Count                                | Total completed projects.                   |
|Internships_Count                             |Number of internships completed.             |
|Certifications_Count                          | Number of certifications earned.            |
|Open_Source_Contributions                     |Open source contribution count.              |    
|GitHub_Contributions                          | GitHub contribution count.                  |
|LinkedIn_Activity_Score                       |Relative LinkedIn activity score.            |
|Hackathons_Participated                       | Number of hackathons attended.              | 
|Competitive_Programming_Rating                |Competitive programming rating (0-2500).     |
|Study_Hours_Per_Week                          |Average study hours per week.                |
|Soft_Skills_Score                             | Soft skills assessment score.               |
|Leadership_Experience                         |Indicates leadership experience (Yes/No).    |
|Extracurricular_Activities                    | Number of extracurricular activities.       |
|Placement_Status                              |Final placement outcome.                     |
|Package_LPA                                   |Annual compensation in Lakhs Per Annum.      |

----

## Target Variables

### Placement_Status

Possible Values:  
* Placed  
* Not Placed  

### Package_LPA

Range:

* 0.00-49.99 LPA  

--- 

## Missing Values

Intentional missing values are present in:

|Column                                         |   Missing Count |
|---------------------------------------------  |   ------------: |
|Open_Source_Contributions                      |             255 |
|LinkedIn_Activity_Score                        |            225  |