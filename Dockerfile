FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=flight_data
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=userpassword

# Expose the default MySQL port
EXPOSE 3306
