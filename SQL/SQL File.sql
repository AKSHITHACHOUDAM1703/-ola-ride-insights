

USE ola_ride_project;



SELECT Booking_Status, COUNT(*) AS rides
FROM ola_rides
GROUP BY Booking_Status
ORDER BY rides DESC;


SELECT *
FROM ola_rides
WHERE Booking_Status = 'Success';


SELECT Vehicle_Type,
       ROUND(AVG(Ride_Distance), 2) AS avg_ride_distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY avg_ride_distance DESC;


SELECT COUNT(*) AS rides_cancelled_by_customers
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';


SELECT Customer_ID,
       COUNT(*) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC, Customer_ID
LIMIT 5;


SELECT COUNT(*) AS driver_cancellations_personal_car
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';


SELECT MAX(Driver_Ratings) AS max_driver_rating,
       MIN(Driver_Ratings) AS min_driver_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';


SELECT *
FROM ola_rides
WHERE Payment_Method = 'UPI';


SELECT Vehicle_Type,
       ROUND(AVG(Customer_Rating), 3) AS avg_customer_rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;


SELECT SUM(Booking_Value) AS total_booking_value_successful
FROM ola_rides
WHERE Booking_Status = 'Success';


SELECT Booking_ID,
       Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';


SELECT v.Vehicle_Type,
       v.successful_rides,
       ROUND(100 * v.successful_rides / t.total_success, 2) AS share_percent
FROM (SELECT Vehicle_Type, COUNT(*) AS successful_rides
      FROM ola_rides
      WHERE Booking_Status = 'Success'
      GROUP BY Vehicle_Type) AS v
CROSS JOIN (SELECT COUNT(*) AS total_success
      FROM ola_rides
      WHERE Booking_Status = 'Success') AS t
ORDER BY v.successful_rides DESC;

 