@echo off
echo Starting phone number processing...

docker-compose build
docker-compose up

echo Processing complete! Check the output directory for results.
pause