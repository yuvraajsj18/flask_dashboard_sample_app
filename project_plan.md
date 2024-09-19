# Flask App Instrumentation and SigNoz Dashboard Project Plan

## 1. Set up the development environment
- [x] Create a new directory for the project
- [x] Set up a virtual environment
- [x] Install necessary dependencies

## 2. Create a sample Flask application
- [x] Create a basic Flask app with the following endpoints:
  - [x] "/" - Home page
  - [x] "/fast" - A fast-responding endpoint
  - [x] "/slow" - An endpoint with artificial delay
  - [x] "/error" - An endpoint that randomly produces errors
- [x] Implement error handling and logging
- [x] Create a configuration file for app settings

## 3. Instrument the Flask app with OpenTelemetry
- [x] Install OpenTelemetry dependencies
- [x] Configure automatic instrumentation
- [x] Add custom instrumentation for specific metrics:
  - [x] Request duration tracking
  - [x] Custom counters and histograms

## 4. Configure the app to send data to SigNoz
- [x] Set up environment variables for SigNoz connection
- [x] Configure the OpenTelemetry exporter

## 5. Run the application and generate some traffic
- [x] Start the Flask server
- [x] Use a script or tool to generate traffic to different endpoints

## 6. Create the dashboard in SigNoz
- [x] Log in to SigNoz
- [x] Create a new dashboard
- [x] Add panels for each metric:
  - [x] Requests Per Second
  - [x] Errors per second
  - [x] Average Response time
  - [x] Request Duration [s] - p90
- [x] Configure each panel with the appropriate queries

## 7. Verify the data in the dashboard
- [x] Ensure all panels are displaying data correctly
- [x] Troubleshoot issues with data collection or display
- [x] Adjust "Request Duration [s] - p90" panel query
