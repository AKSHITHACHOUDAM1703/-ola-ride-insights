-- =====================================================================
-- OLA Ride Insights - 10 SQL analysis queries (MySQL)
-- Database : ola_ride_project
-- Table    : ola_rides  (loaded from Data/ola_cleaned.csv by import_to_mysql.py)
-- Rows     : 103,024
-- =====================================================================

USE ola_ride_project;

-- ---------------------------------------------------------------------
-- (Optional) Convert text columns to proper date/time types.
-- The import script loads Date and Time as text. Run once if you want
-- real DATETIME / TIME columns.
-- ---------------------------------------------------------------------
-- ALTER TABLE ola_rides MODIFY `Date` DATETIME;
-- ALTER TABLE ola_rides MODIFY `Time` TIME;

-- ---------------------------------------------------------------------
-- Sanity check: row count and booking statuses
-- Expected: 103,024 rows | Success 63,967 | Canceled by Driver 18,434
--           Canceled by Customer 10,499 | Driver Not Found 10,124
-- ---------------------------------------------------------------------
SELECT Booking_Status, COUNT(*) AS rides
FROM ola_rides
GROUP BY Booking_Status
ORDER BY rides DESC;

-- ---------------------------------------------------------------------
-- Q1. Retrieve all successful bookings
-- Expected: 63,967 rows
-- ---------------------------------------------------------------------
SELECT *
FROM ola_rides
WHERE Booking_Status = 'Success';

-- ---------------------------------------------------------------------
-- Q2. Average ride distance for each vehicle type
-- Cancelled rides have distance 0, so only successful rides are used.
-- Expected: eBike 25.15, Prime Plus 25.03, Prime Sedan 25.01,
--           Mini 24.98, Bike 24.93, Prime SUV 24.88, Auto 10.04
-- ---------------------------------------------------------------------
SELECT Vehicle_Type,
       ROUND(AVG(Ride_Distance), 2) AS avg_ride_distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY avg_ride_distance DESC;

-- ---------------------------------------------------------------------
-- Q3. Total number of rides cancelled by customers
-- Expected: 10,499
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS rides_cancelled_by_customers
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';

-- ---------------------------------------------------------------------
-- Q4. Top 5 customers who booked the highest number of rides
-- Expected: CID954071 (5 rides), then customers with 4 rides each
-- ---------------------------------------------------------------------
SELECT Customer_ID,
       COUNT(*) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC, Customer_ID
LIMIT 5;

-- ---------------------------------------------------------------------
-- Q5. Rides cancelled by drivers due to personal and car-related issues
-- Expected: 6,542
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS driver_cancellations_personal_car
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- ---------------------------------------------------------------------
-- Q6. Maximum and minimum driver ratings for Prime Sedan bookings
-- Expected: max 5.0, min 3.0
-- ---------------------------------------------------------------------
SELECT MAX(Driver_Ratings) AS max_driver_rating,
       MIN(Driver_Ratings) AS min_driver_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';

-- ---------------------------------------------------------------------
-- Q7. Retrieve all rides where payment was made using UPI
-- Expected: 25,881 rows
-- ---------------------------------------------------------------------
SELECT *
FROM ola_rides
WHERE Payment_Method = 'UPI';

-- ---------------------------------------------------------------------
-- Q8. Average customer rating per vehicle type
-- Expected: Prime Plus 4.009, Prime Sedan 4.002, Prime SUV 3.999,
--           Auto 3.999, Mini 3.998, Bike 3.993, eBike 3.988
-- ---------------------------------------------------------------------
SELECT Vehicle_Type,
       ROUND(AVG(Customer_Rating), 3) AS avg_customer_rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

-- ---------------------------------------------------------------------
-- Q9. Total booking value of rides completed successfully
-- Expected: 35,080,467
-- ---------------------------------------------------------------------
SELECT SUM(Booking_Value) AS total_booking_value_successful
FROM ola_rides
WHERE Booking_Status = 'Success';

-- ---------------------------------------------------------------------
-- Q10. All incomplete rides along with the reason
-- Expected: 3,926 rows (Customer Demand 1,601, Vehicle Breakdown 1,591,
--           Other Issue 734)
-- ---------------------------------------------------------------------
SELECT Booking_ID,
       Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';

-- ---------------------------------------------------------------------
-- Bonus (uses a JOIN): successful rides per vehicle type, with each
-- vehicle's share of all successful rides
-- ---------------------------------------------------------------------
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
