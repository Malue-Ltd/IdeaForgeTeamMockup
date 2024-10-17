using System;
using System.Data.SqlClient;
using System.IO;

namespace FileDatabaseLookup
{
    class Program
    {
        static void Main(string[] args)
        {
            string filePath = $@"D:\OneDrive\Jim - Malue Ltd\OneDrive - Malue Ltd\Malue Resources\MedicalProducts\VascularAccesProductsAndScan\file.txt";
            string connectionString = "data source=sql-maluepoc-shared-westeu.database.windows.net;initial catalog=nhsproducts; user id=maluepoc;password=lead2gold!";


            try
            {
                using (StreamReader reader = new StreamReader(filePath))
                {
                    string line;

                    while ((line = reader.ReadLine()) != null)
                    {
                        // Split each line by tabs
                        string[] values = line.Split('\t');
                        
                        if (values.Length < 3)
                        {
                            Console.WriteLine("Invalid line format, skipping line.");
                            continue;
                        }

                        string key = values[3]; // Third value in the line

                        // Lookup record in the database
                        LookupProduct(connectionString, key);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred: " + ex.Message);
            }
        }

        static void LookupProduct(string connectionString, string key)
        {
            string query = "SELECT * FROM [products] WHERE [mpc] like @key or [gtin] like @key";

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                SqlCommand command = new SqlCommand(query, connection);
                command.Parameters.AddWithValue("@key", key);

                try
                {
                    connection.Open();

                    using (SqlDataReader reader = command.ExecuteReader())
                    {
                        if (reader.HasRows)
                        {
                            while (reader.Read())
                            {
                                // Replace with actual columns in the products table
                                Console.WriteLine($"Product ID: {reader["ProductID"]}, Name: {reader["ProductName"]}");
                            }
                        }
                        else
                        {
                            Console.WriteLine($"No product found with key: {key}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Database error: " + ex.Message);
                }
            }
        }
    }
}
